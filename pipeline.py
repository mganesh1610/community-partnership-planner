"""Public-data community planning and healthcare market context. Python standard library."""
from __future__ import annotations
import csv
import hashlib
import html
import json
import math
import sqlite3
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data/raw"
OUT = ROOT / "results"
SCHOOL_BASE = "https://nces.ed.gov/opengis/rest/services/K12_School_Locations/EDGE_GEOCODE_PUBLICSCH_2324/MapServer/0/query"
SPORT_BASE = "https://maps.phoenix.gov/pub/rest/services/Public/ParksOpenData/MapServer/7/query"
CMS_BASE = "https://data.cms.gov/provider-data/api/1/datastore/query/xubh-q36u/0"

def get_json(name, base, params):
    url = base + "?" + urllib.parse.urlencode(params)
    path = RAW / (name + ".json")
    if not path.exists():
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        path.write_bytes(data)
    data = path.read_bytes()
    parsed = json.loads(data)
    if "error" in parsed:
        raise ValueError(parsed["error"])
    return parsed, {"name": name, "url": url, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}

def distance_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(math.radians(lon2-lon1)/2)**2
    return 6371.0088 * 2 * math.asin(min(1, math.sqrt(a)))

def valid_coord(lat, lon):
    return isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and 30 <= lat <= 38 and -115.5 <= lon <= -108.5

def allocate_budget(weights, budget_cents):
    """Largest remainder allocation conserves whole cents, including tied weights."""
    if not weights or any(v < 0 for v in weights.values()) or sum(weights.values()) <= 0 or budget_cents < 0:
        raise ValueError("nonnegative weights and budget with positive total required")
    total = sum(weights.values())
    raw = {k: v / total * budget_cents for k, v in weights.items()}
    result = {k: math.floor(v) for k, v in raw.items()}
    for k in sorted(weights, key=lambda k: (-(raw[k]-result[k]), k))[:budget_cents-sum(result.values())]:
        result[k] += 1
    return result

def nearest_catchments(schools, venues, radius):
    if radius <= 0 or not venues:
        raise ValueError("positive radius and at least one venue required")
    assigned = []
    for school in schools:
        distances = [(distance_km(school["lat"], school["lon"], v["lat"], v["lon"]), v["venue_id"]) for v in venues]
        distance, venue = min(distances)
        if distance <= radius:
            assigned.append({"school_id": school["school_id"], "venue_id": venue, "distance_km": round(distance, 4)})
    return assigned

def save_csv(filename, rows, fields):
    with (OUT / filename).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)
    provenance, schools = [], []
    offset = 0
    while True:
        response, source = get_json(f"schools_{offset}", SCHOOL_BASE, {"where": "STATE='AZ'", "outFields": "NCESSCH,STFIP,CNTY,NMCNTY,LAT,LON,SCHOOLYEAR", "returnGeometry": "false", "orderByFields": "NCESSCH", "resultOffset": offset, "resultRecordCount": 2000, "f": "json"})
        provenance.append(source)
        features = response["features"]
        for feature in features:
            row = feature["attributes"]
            schools.append({"school_id": row["NCESSCH"], "county_fips": row["CNTY"], "county": row["NMCNTY"].upper().removesuffix(" COUNTY"), "lat": row["LAT"], "lon": row["LON"], "school_year": row["SCHOOLYEAR"]})
        if not response.get("exceededTransferLimit"):
            break
        if not features:
            raise ValueError("pagination indicated more rows but returned none")
        offset += len(features)
    excluded = [s for s in schools if not s['county_fips'].startswith('04')]
    source_school_rows = len(schools)
    schools = [s for s in schools if s['county_fips'].startswith('04')]
    county_lookup = {s['county'].replace(' ',''):s['county'] for s in schools}
    save_csv('geography_exclusions.csv', [{'school_id':s['school_id'],'county_fips':s['county_fips'],'reason':'Administrative AZ school with county geocode outside AZ'} for s in excluded], ['school_id','county_fips','reason'])
    response, source = get_json("sports", SPORT_BASE, {"where": "1=1", "outFields": "OBJECTID,COMPLEX_NAME", "returnGeometry": "true", "outSR": 4326, "f": "json"})
    provenance.append(source)
    if response.get("exceededTransferLimit"):
        raise ValueError("sports response truncated")
    venues = [{"venue_id": str(f["attributes"]["OBJECTID"]), "venue_name": f["attributes"]["COMPLEX_NAME"], "lat": f["geometry"]["y"], "lon": f["geometry"]["x"]} for f in response["features"]]
    response, source = get_json("hospitals", CMS_BASE, {"limit": 500, "offset": 0, "conditions[0][property]": "state", "conditions[0][value]": "AZ", "conditions[0][operator]": "="})
    provenance.append(source)
    if len(response["results"]) != response["count"]:
        raise ValueError("hospital response truncated")
    hospitals = [{"facility_id": r["facility_id"], "county": county_lookup.get(r["countyparish"].upper().removesuffix(" COUNTY").replace(' ',''),r["countyparish"]), "hospital_type": r["hospital_type"], "rating": r["hospital_overall_rating"]} for r in response["results"] if r["state"] == "AZ"]
    assert len({s["school_id"] for s in schools}) == len(schools)
    assert len({v["venue_id"] for v in venues}) == len(venues)
    assert all(valid_coord(s["lat"], s["lon"]) for s in schools)
    assert all(valid_coord(v["lat"], v["lon"]) for v in venues)
    assert len({h["facility_id"] for h in hospitals}) == len(hospitals)
    assigned = nearest_catchments(schools, venues, 10)
    overlaps = sum(sum(distance_km(s["lat"], s["lon"], v["lat"], v["lon"]) <= 10 for v in venues) for s in schools)
    counts = Counter(s["county"] for s in schools)
    hospital_counts = Counter(h["county"] for h in hospitals)
    budgets = allocate_budget(dict(counts), 10000000)
    markets = [{"county": c, "schools": counts[c], "hospitals": hospital_counts[c], "school_share": round(counts[c]/len(schools), 8), "planning_budget_cents": budgets[c]} for c in sorted(counts, key=lambda c: (-counts[c], c))]
    with sqlite3.connect(ROOT / "data/community.db") as db:
        db.executescript("DROP TABLE IF EXISTS school; DROP TABLE IF EXISTS venue; DROP TABLE IF EXISTS catchment; DROP TABLE IF EXISTS hospital; CREATE TABLE school(school_id TEXT PRIMARY KEY, county_fips TEXT, county TEXT, lat REAL, lon REAL, school_year TEXT); CREATE TABLE venue(venue_id TEXT PRIMARY KEY, venue_name TEXT, lat REAL, lon REAL); CREATE TABLE catchment(school_id TEXT PRIMARY KEY REFERENCES school(school_id), venue_id TEXT REFERENCES venue(venue_id), distance_km REAL CHECK(distance_km BETWEEN 0 AND 10)); CREATE TABLE hospital(facility_id TEXT PRIMARY KEY, county TEXT, hospital_type TEXT, rating TEXT);")
        db.executemany("INSERT INTO school VALUES(:school_id,:county_fips,:county,:lat,:lon,:school_year)", schools)
        db.executemany("INSERT INTO venue VALUES(:venue_id,:venue_name,:lat,:lon)", venues)
        db.executemany("INSERT INTO catchment VALUES(:school_id,:venue_id,:distance_km)", assigned)
        db.executemany("INSERT INTO hospital VALUES(:facility_id,:county,:hospital_type,:rating)", hospitals)
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        fk = db.execute("PRAGMA foreign_key_check").fetchall()
        sql_schools = db.execute("SELECT COUNT(*) FROM school").fetchone()[0]
        sql_unique = db.execute("SELECT COUNT(DISTINCT school_id) FROM catchment").fetchone()[0]
    checks = {"unique_school_keys": len(schools)==len({s['school_id'] for s in schools}), "unique_venue_keys": len(venues)==len({v['venue_id'] for v in venues}), "valid_coordinates": all(valid_coord(s['lat'],s['lon']) for s in schools+venues), "budget_conserves_cents": sum(budgets.values())==10000000, "one_school_one_venue": len(assigned)==len({s['school_id'] for s in assigned}), "sql_source_parity": sql_schools==len(schools), "sql_catchment_parity": sql_unique==len(assigned), "sqlite_integrity": integrity=='ok' and not fk, "hospital_county_coverage": set(hospital_counts).issubset(counts), "all_15_counties": len(counts)==15}
    if not all(checks.values()):
        raise ValueError(checks)
    sensitivity = [{"radius_km": r, "unique_schools": len(nearest_catchments(schools, venues, r))} for r in (5,10,15)]
    venue_counts = Counter(a["venue_id"] for a in assigned)
    save_csv("county_markets.csv", markets, list(markets[0]))
    save_csv("venue_catchments.csv", [dict(v, unique_schools_10km=venue_counts[v['venue_id']]) for v in venues], list(venues[0])+["unique_schools_10km"])
    save_csv("radius_sensitivity.csv", sensitivity, list(sensitivity[0]))
    metrics = {"executed_at_utc": datetime.now(timezone.utc).isoformat(), "source_school_rows": source_school_rows, "excluded_out_of_state_geocodes": len(excluded), "schools": len(schools), "sports_complexes": len(venues), "counties": len(counts), "arizona_hospitals": len(hospitals), "unique_schools_10km": len(assigned), "naive_school_venue_pairs_10km": overlaps, "overlap_pairs_removed": overlaps-len(assigned), "checks_passed": sum(checks.values()), "checks": checks, "sensitivity": sensitivity, "provenance": provenance}
    (OUT / "validation.json").write_text(json.dumps(metrics, indent=2)+"\n")
    table = "".join(f"<tr><td>{html.escape(r['county'])}</td><td>{r['schools']:,}</td><td>{r['hospitals']}</td><td>${r['planning_budget_cents']/100:,.2f}</td></tr>" for r in markets)
    (OUT / "review.html").write_text(f'<!doctype html><html><meta charset="utf-8"><title>Community partnership planning</title><style>body{{font:16px Arial;max-width:1000px;margin:40px auto;color:#20272c}}h1,h2{{color:#173b55}}table{{border-collapse:collapse;width:100%}}td,th{{padding:10px;text-align:left;border-bottom:1px solid #ddd}}.metrics{{font-size:22px}}</style><h1>Community partnership planning</h1><p class="metrics">{len(schools):,} schools · {len(venues)} sports complexes · {len(counts)} counties</p><p>Nearest-venue assignment identifies {len(assigned):,} unique schools within 10 km and removes {overlaps-len(assigned):,} overlapping school–venue pairs.</p><h2>County planning context</h2><p>County-level school catchments, CMS hospital coverage, and largest-remainder budget allocations ($100,000 total conserved to the cent).</p><table><tr><th>County</th><th>Schools</th><th>CMS hospitals</th><th>Planned allocation</th></tr>{table}</table><h2>Launch readiness</h2><p>Confirm clinician capacity, referral access, service availability, web content, brand approval, tracking, family experience, and partner deliverables before media release. Use the supplied review templates and readiness checks.</p></html>')
    print(json.dumps({k:v for k,v in metrics.items() if k not in ('provenance','checks','sensitivity')}, indent=2))

if __name__ == "__main__":
    main()

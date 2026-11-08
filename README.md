# Community Partnership Planner

A consumer-strategy and spatial catchment planning system combining official school geography, municipal sports facilities, and hospital roster context using the Python standard library and SQLite.

## Executed results

The run read 2,613 administrative-state school records, retained **2,612 geocoded Arizona schools**, and quarantined **one school with an out-of-state county geocode**. It joined **7 municipal sports complexes**, **108 CMS hospitals**, and **15 counties**. Nearest-venue attribution identified **613 unique schools within 10 km** and removed **600 overlapping school–venue pairs** from the naive 1,213-pair count. All **10 source/SQL/geography/budget checks** and **8 boundary tests** passed.

## Run

```sh
python pipeline.py
python -m unittest -v
```

The first command downloads versioned school locations and current public municipal/CMS records, caches the original bytes locally, records SHA-256 hashes, and writes a SQLite database, aggregate CSVs, and an HTML strategy review. Cached raw inputs are ignored by Git. Delete the raw cache intentionally to refresh.

## Architecture

Official APIs → immutable raw JSON cache → school/county/venue schema checks → county alias normalization → county-geocode exception log → nearest-venue catchments → constrained SQLite tables → county planning context and venue shortlist → cents-conserving budget allocation → review artifacts.

`pipeline.py` owns ingestion and methods; `test_pipeline.py` covers arithmetic, geographic distance, overlap, and invalid inputs. `results/validation.json` owns executed counts, hashes, and checks. `results/review.html` presents the results without requiring a server. See [schema and source notes](docs/schema.md) and the [marketing review runbook](docs/strategy_runbook.md).

## Public data

- **Primary school data:** [NCES EDGE Public School Locations 2023–24](https://nces.ed.gov/programs/edge/geographic/schoollocations), [query service](https://nces.ed.gov/opengis/rest/services/K12_School_Locations/EDGE_GEOCODE_PUBLICSCH_2324/MapServer/0).
- **Primary facility data:** [City of Phoenix Sports Complexes](https://maps.phoenix.gov/pub/rest/services/Public/ParksOpenData/MapServer/7).
- **Healthcare context:** [CMS Hospital General Information](https://data.cms.gov/provider-data/dataset/xubh-q36u), filtered to Arizona.
- **Backup school source:** NCES EDGE prior school-year locations from the same official [school location catalog](https://nces.ed.gov/programs/edge/geographic/schoollocations), using an explicit year parameter and schema adapter.
- **Backup community source:** [City basketball court locations](https://maps.phoenix.gov/pub/rest/services/Public/ParksOpenData/MapServer/0), using a court-to-venue rollup.
- **Backup hospital transport:** [HealthData.gov hospital roster](https://healthdata.gov/d/n7m7-8qpq).

Only aggregate outputs and provenance metadata are committed.

## Spatial catchment and budget methods

Haversine distance uses an Earth radius of 6,371.0088 km and a configured 10 km radius. Each school is assigned to its nearest qualifying venue; equal-distance ties resolve by venue ID. The 5/10/15 km sensitivity output quantifies catchment coverage across radius thresholds.

County budget allocations use school-location weights, with largest-remainder allocation conserving $100,000 exactly to the cent. `docs/experience_backing.md` maps analytics, content, agency, and activation workflows to runnable components.

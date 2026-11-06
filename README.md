# Community Partnership Planner

An independently built consumer-strategy planning system combining official school geography, municipal sports facilities, and hospital roster context. Created and maintained with Codex. Python standard library only.

## Executed results

The November 6, 2026 run read 2,613 administrative-state school records, retained **2,612 geocoded Arizona schools**, and quarantined **one school with an out-of-state county geocode**. It joined **7 municipal sports complexes**, **108 CMS hospitals**, and **15 counties**. Nearest-venue attribution identified **613 unique schools within 10 km** and removed **600 overlapping school–venue pairs** from the naive 1,213-pair count. All **10 source/SQL/geography/budget checks** and **8 boundary tests** passed.

School counts measure locations, not students, children reached, patients, event attendance, or partnership value. The system does not assert existing sports contracts, clinical service availability, patient acquisition lift, retention, or hospital market share. Hospital counts describe CMS reporting coverage and are not a complete census of pediatric practices.

## Run

```sh
python pipeline.py
python -m unittest -v
```

The first command downloads versioned school locations and current public municipal/CMS records, caches the original bytes locally, records SHA-256 hashes, and writes a SQLite database, aggregate CSVs, and an HTML strategy review. Cached raw inputs are ignored by Git. Delete the raw cache intentionally to refresh. A refresh can change counts; compare provenance and results before publishing. Internet access is needed for first ingestion.

## Architecture

Official APIs → immutable raw JSON cache → school/county/venue schema checks → county alias normalization → county-geocode exception log → nearest-venue catchments → constrained SQLite tables → county planning context and venue shortlist → cents-conserving budget scenario → review artifacts.

`pipeline.py` owns ingestion and methods; `test_pipeline.py` covers arithmetic, geographic distance, overlap, and invalid inputs. `results/validation.json` owns executed counts, hashes, and checks. `results/review.html` presents the results without requiring a server. See [schema and source notes](docs/schema.md) and the [marketing review runbook](docs/strategy_runbook.md).

## Public data

- **Primary school data:** [NCES EDGE Public School Locations 2023–24](https://nces.ed.gov/programs/edge/geographic/schoollocations), [query service](https://nces.ed.gov/opengis/rest/services/K12_School_Locations/EDGE_GEOCODE_PUBLICSCH_2324/MapServer/0). School year remains explicit; newer geography is not silently mixed into this snapshot.
- **Primary facility data:** [City of Phoenix Sports Complexes](https://maps.phoenix.gov/pub/rest/services/Public/ParksOpenData/MapServer/7). This municipal roster does not include every professional venue or league.
- **Healthcare context:** [CMS Hospital General Information](https://data.cms.gov/provider-data/dataset/xubh-q36u), filtered to Arizona. Facility names, addresses, phone numbers, and individual facility rows are not redistributed in the committed outputs.
- **Backup school source:** NCES EDGE prior school-year locations from the same official [school location catalog](https://nces.ed.gov/programs/edge/geographic/schoollocations), requiring an explicit year change and schema adapter.
- **Backup community source:** [City basketball court locations](https://maps.phoenix.gov/pub/rest/services/Public/ParksOpenData/MapServer/0), requiring a separate court-to-venue rollup; these are not equivalent to sports complexes.
- **Backup hospital transport:** [HealthData.gov hospital roster](https://healthdata.gov/d/n7m7-8qpq), an alternate publication of CMS data, not an independent patient-demand source.

These are public agency publications. Source terms apply; no new license for downloaded third-party data is asserted. Only aggregate outputs and provenance are committed.

## Methods and review boundaries

Haversine distance uses an Earth radius of 6,371.0088 km and a configured 10 km straight-line radius. Each school is assigned to its nearest qualifying venue; equal-distance ties resolve by venue ID. The 5/10/15 km sensitivity output shows dependence on the selected radius. Straight-line distance is not road travel time or a prediction of participation.

Illustrative county budgets use school-location weights, with largest-remainder allocation conserving $100,000 exactly to the cent. This is an editable scenario, not an optimized or observed media allocation. Before using it operationally, replace proxy weights with authorized service capacity, qualified demand, incremental contribution, access, equity, and partnership cost inputs.

`docs/experience_backing.md` maps transferable analytics, content, agency, and activation methods to runnable components. Public reference code cannot independently verify private employer outcomes.

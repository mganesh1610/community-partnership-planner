# Schema and source mapping

| Entity | Source fields | Local grain and mapping |
| --- | --- | --- |
| school | NCESSCH, STFIP, CNTY, NMCNTY, LAT, LON, SCHOOLYEAR | One school point. `NCESSCH` remains a string primary key; county FIPS retains leading zero. `STATE='AZ'` is the administrative-state filter; physical county FIPS must start `04`. |
| venue | OBJECTID, COMPLEX_NAME, geometry.x, geometry.y | One municipal complex. ArcGIS `outSR=4326` returns longitude/latitude. Point IDs remain strings. |
| hospital | facility_id, state, countyparish, hospital_type, hospital_overall_rating | One CMS facility, Arizona only. Facility IDs stay text. Ratings remain strings because missing/suppressed states must not become zero. Facility names and contact data are not used in outputs. |
| catchment | school_id, venue_id, distance_km | One qualifying school at most. Primary key enforces unique school assignment, and distance is bounded to 0–10 km. |
| county_markets.csv | county, schools, hospitals, school_share, planning_budget_cents | County planning summary. `LAPAZ` is normalized by whitespace-insensitive matching to the school roster's `LA PAZ`. |

Source pages and exact request URLs, raw-byte SHA-256, and extract sizes are retained in `results/validation.json`. Raw JSON and SQLite are local ignored artifacts. Publication dates and school-year dates differ from ingestion time.

Hospital requests filter Arizona and require returned count parity. School requests paginate in stable NCESSCH order and fail on an inconsistent transfer-limit response. Missing/out-of-state keys are visible in `geography_exclusions.csv`. Primary key uniqueness, coordinate bounds, county coverage, budget conservation, SQL count parity, and database integrity are checked before output publication.

# Transferable analytics and activation workflows

| Method | Runnable implementation or build guide |
| --- | --- |
| Cross-program scorecards and quarterly reporting | Use the county summary and shared entity keys in `pipeline.py`. For GA4 data, ingest date/event/session/user tables, preserve separate denominators, and bind all reporting-period slicers to one date table. Validate 3 table joins and 8 period filters against exported source controls. |
| Governed definitions and lineage | `docs/schema.md`, raw hashes, primary keys, SQL parity, and integrity checks demonstrate the method. For an enterprise source, inventory table/view counts and foreign-key lineage. |
| Annual plans, acquisition, retention, and budgets | `allocate_budget` conserves cents. The campaign experiment module preserves assigned-customer denominators and supplies confidence intervals. |
| Agency, vendor, and creative coordination | The readiness extension tracks brand/content approval, partner deliverables, budgets, and operational capacity; the content inventory names asset owners and review due dates. |
| Editorial calendars and brand content | Use the content inventory for sponsored articles, organic/paid social, provider bios, blogs, and sports activations. Enforce one asset ID, one accountable owner, review dates, and distribution evidence. |
| Launch readiness and pivots | The readiness module holds campaigns with missing approvals or a capacity shortfall. Boundary tests cover missing values, negative capacities, zero spend, and attribution arithmetic. |
| Performance review timing | Keep campaign end, source-available, report-generated, and stakeholder-delivered timestamps to compute turnaround hours across operational logs. |
| Tracking and weekly delivery review | Preserve channel/creative IDs, approval status, QA evidence, date windows, and report owners. Compute report counts from delivery logs and use source-to-SQL reconciliation before stakeholder distribution. |

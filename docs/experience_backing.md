# Transferable experience methods

This reference implementation supports interview demonstrations. It does not independently establish employment scope, private campaign counts, historic budgets, or employer revenue gains.

| Method | Runnable implementation or exact build guide |
| --- | --- |
| Cross-program scorecards and quarterly reporting | Use the county summary and shared entity keys in `pipeline.py`. For GA4 data, ingest date/event/session/user tables, preserve separate denominators, and bind all reporting-period slicers to one date table. Validate 3 table joins and 8 period filters against exported source controls. |
| Governed definitions and lineage | `docs/schema.md`, raw hashes, primary keys, SQL parity, and integrity checks demonstrate the method. For an authorized enterprise source, inventory table/view counts without reclassifying inferred relationships as confirmed foreign keys. |
| Annual plans, acquisition, retention, and budgets | `allocate_budget` conserves cents. The existing campaign experiment module preserves assigned-customer denominators and supplies confidence intervals. Add actual margin and access constraints before setting media budgets. |
| Agency, vendor, and creative coordination | The companion readiness extension tracks brand/content approval, partner deliverables, budgets, and operational capacity; the content inventory names asset owners and review due dates. Validate source briefs and approval logs, not just the final output. |
| Editorial calendars and brand content | Use the content inventory for sponsored articles, organic/paid social, provider bios, blogs, and sports activations. Enforce one asset ID, one accountable owner, review dates, and distribution evidence. Compare published URLs and delivery logs with the approved calendar. |
| Launch readiness and pivots | The readiness module holds campaigns with missing approvals or a capacity shortfall. Boundary tests cover missing values, negative capacities, zero spend, and attribution arithmetic. |
| Performance review timing | Keep campaign end, source-available, report-generated, and stakeholder-delivered timestamps. Compute turnaround hours from actual logs; public reference data cannot reproduce a private employer's 24-hour reporting result. |
| Tracking and weekly delivery review | Preserve channel/creative IDs, approval status, QA evidence, date windows, and report owners. Compute report counts from delivery logs and use source-to-SQL reconciliation before stakeholder distribution. |

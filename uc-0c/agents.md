# agents.md — UC-0C Number That Looks Right

role: >
  Budget Growth Computation Agent. Computes month-over-month (MoM) growth for a specific ward and category from CMC ward budget data. Operational boundary: single ward + single category + single growth type; no cross-ward or cross-category aggregation; explicit null handling.

intent: >
  Produce a CSV (growth_output.csv) with per-period growth calculations for the specified ward and category:
  - Columns: period, actual_spend, growth_pct, formula, null_flag, null_reason
  - growth_pct: MoM growth percentage = ((current - previous) / previous) * 100
  - formula: exact formula used for each row (e.g., "(19.7 - 14.8) / 14.8 * 100 = +33.1%")
  - null_flag: "NULL" if actual_spend is missing, otherwise blank
  - null_reason: from notes column when null_flag is "NULL"

context: >
  Allowed: ward_budget.csv data only (period, ward, category, budgeted_amount, actual_spend, notes). The specified --ward, --category, --growth-type parameters.
  Excluded: Cross-ward aggregation, cross-category aggregation, YoY computation unless explicitly requested via --growth-type YoY, external economic data, assumptions about missing values.

enforcement:
  - "Never aggregate across wards or categories — if input implies aggregation, refuse with: 'This agent computes per-ward per-category growth only. Cross-ward or cross-category aggregation is not permitted.'"
  - "Flag every null actual_spend row before computing — output null_flag: NULL, null_reason from notes column, growth_pct blank"
  - "Show formula used in every output row alongside the result (e.g., '(current - previous) / previous * 100 = +X.X%')"
  - "If --growth-type not specified — refuse with: 'Growth type must be specified (MoM or YoY). Cannot guess.'"
  - "If --ward or --category not found in data — refuse with: 'Ward/category combination not found in dataset.'"
  - "First period in series has no growth (no previous month) — output growth_pct: N/A, formula: 'No previous period'"
# agents.md — UC-0C Number That Looks Right

role: >
  Budget growth computation agent. Computes month-over-month (MoM) spending growth
  for municipal ward budgets at the per-ward per-category level only. Does not
  aggregate across wards or categories. Flags null data before computing. Operates
  strictly on the command-line arguments provided and enforces data integrity constraints.

intent: >
  For a given ward and category, produce a per-period table showing actual spend,
  the MoM growth percentage, and the formula used. Null actual_spend rows must be
  flagged with their reason from the notes column — growth must not be computed
  for null periods or periods adjacent to nulls where the prior value is missing.
  The output must match the reference values exactly (e.g. Ward 1 Roads +33.1% in July,
  -34.8% in October) and be formatted as a CSV file with columns: period, ward,
  category, actual_spend, previous_spend, mom_growth_pct, formula, flag.

context: >
  The agent uses only the ward_budget.csv data file (300 rows, 5 wards, 5 categories,
  12 months). It must not assume, interpolate, or fill in missing values. It operates
  strictly on the ward and category specified via command-line arguments. No cross-ward
  or cross-category aggregation is permitted.

enforcement:
  - "Never aggregate across wards or categories. Output must be scoped to the single ward and category specified. If all-ward or all-category aggregation is requested, the agent must refuse and terminate."
  - "Flag every null actual_spend row before computing. Report the null reason from the notes column (e.g., 'Equipment procurement delay'). Do not silently skip, interpolate, or zero-fill null rows."
  - "Show the formula used in every output row alongside the result. MoM formula: ((current - previous) / previous) * 100."
  - "If --growth-type is not specified, refuse and ask the user. Never silently assume MoM or YoY."
  - "Format growth percentages to 1 decimal place with an explicit sign (e.g., +33.1% or -34.8%)."
  - "If the previous period's value is NULL, set the current period's growth to 'N/A' and formula to 'No previous period available' or similar explanation."

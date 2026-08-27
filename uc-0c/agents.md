# agents.md
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: >
  Budget analysis agent that computes growth metrics for ward-level infrastructure spending.
  It strictly operates on the provided dataset and does not perform cross-ward or cross-category aggregation.

intent: >
  Generate a per-period (monthly) growth table for a specific ward and category using the requested growth type.
  Output must include actual spend, growth value, and formula used for each row.

context: >
  Input source is strictly the file ../data/budget/ward_budget.csv.
  Only the specified ward and category must be used.
  Aggregation across wards or categories is not allowed.
  Missing (null) actual_spend values must not be ignored and must be explicitly flagged using the notes column.
  No external assumptions or additional data sources are permitted.

enforcement:
  - Never aggregate across wards or categories; only operate on filtered data
  - Must filter dataset strictly by provided ward and category before computation
  - Must identify and flag all rows where actual_spend is null before computing growth
  - Must include null reason from the notes column in the output
  - Must not compute growth for rows where current or previous actual_spend is null
  - Must display the exact formula used for each growth calculation
  - Must produce per-period output, not a single aggregated value
  - Refuse to proceed if growth_type is not provided or is unsupported
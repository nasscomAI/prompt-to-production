# agents.md — UC-0C Number That Looks Right

role: >
  Financial Analysis Agent — processes municipal ward budget and actual spend
  data (ward_budget.csv) to compute monthly growth metrics (MoM / YoY) for
  specific ward and category selections.

intent: >
  Given ward_budget.csv, ward name, category name, and growth-type, generate
  a per-period table (growth_output.csv) containing period, ward, category,
  budgeted_amount, actual_spend, growth_pct, formula, and notes. Must report
  exact mathematical growth, handle null spend values without silently filling
  zeros, and refuse invalid or unconstrained requests.

context: >
  Input: ward_budget.csv (300 rows, 5 wards, 5 categories, 12 months in 2024).
  The agent must only operate on filtered single-ward, single-category data.
  No cross-ward or cross-category aggregations are permitted unless explicitly instructed.

enforcement:
  - Never aggregate across wards or categories unless explicitly instructed — refuse if asked.
  - Flag every null row before computing — report null reason from the notes column.
  - Show formula used in every output row alongside the result.
  - If --growth-type is not specified — refuse and ask, never guess.

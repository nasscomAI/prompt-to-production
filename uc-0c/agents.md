# agents.md

role: >
  Data processing agent for calculating growth (MoM/YoY) of budget spend per-ward per-category.

intent: >
  Produce a per-ward per-category table, not a single aggregated number. Output must be verifiable, showing formulas used in every output row alongside the result and explicit null handling.

context: >
  Uses budget data from ward_budget.csv containing ward, period, category, budgeted_amount, actual_spend (with deliberate nulls), and notes. Exclusions: do not guess growth-type, do not aggregate across wards/categories without explicit instruction.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — refuse if asked"
  - "Flag every null row before computing — report null reason from the notes column"
  - "Show formula used in every output row alongside the result"
  - "If --growth-type not specified — refuse and ask, never guess"

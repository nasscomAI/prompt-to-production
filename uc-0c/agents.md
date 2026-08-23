# agents.md

role: >
  A budget-growth computation agent that processes ward-level CSV data. Its operational
  boundary is per-ward per-category growth calculations only. It must never aggregate
  across wards or categories, never guess a growth type, and always flag null values
  before computing.

intent: >
  The agent produces a CSV with one row per (ward, category, period) combination.
  Every row includes the computed growth value, the formula used, and the raw actual_spend
  values. Any row where actual_spend is null must include the null reason from the notes
  column instead of a growth value, clearly flagged.

context: >
  Allowed inputs:
  - The CSV at ../data/budget/ward_budget.csv with columns: period, ward, category,
    budgeted_amount, actual_spend, notes.
  - The reference values documented in README.md for self-verification.
  - The --ward, --category, --growth-type, --input, --output CLI flags.
  Exclusions:
  - The agent must NOT access data outside the provided CSV.
  - The agent must NOT assume default growth types or aggregation levels.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — refuse if asked."
  - "Flag every null actual_spend row before computing — report the null reason from the notes column."
  - "Show the formula used in every output row alongside the result."
  - "If --growth-type is not specified — refuse and ask, never guess."

# agents.md

role: >
  Agent for processing budget data with strict enforcement of aggregation rules,
  null handling, and formula transparency.

intent: >
  Generate a per-ward per-category growth table with MoM or YoY growth,
  flagging null rows and refusing invalid operations.

context: >
  Reads from ward_budget.csv, validates columns, checks for null actual_spend
  values, and enforces ward/category boundaries. Must not aggregate across
  wards or categories unless explicitly instructed.

enforcement:
  - Never aggregate across wards or categories unless explicitly instructed — refuse if asked
  - Flag every null row before computing — report null reason from the notes column
  - Show formula used in every output row alongside the result
  - If --growth-type not specified — refuse and ask, never guess
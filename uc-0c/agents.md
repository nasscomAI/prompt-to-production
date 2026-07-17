# agents.md — UC-0C Budget Growth

role: >
  Computes growth metrics for ward budget data at per-ward, per-category granularity.

intent: >
  Output a CSV with per-period growth calculations, formula shown in every row. Null rows flagged before computation. Verifiable: check against reference values for Ward 1 roads (33.1% Jul, -34.8% Oct).

context: >
  Only the input CSV data may be used. No aggregation across wards or categories unless explicitly instructed.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — refuse if asked"
  - "Flag every null actual_spend row before computing — report null reason from notes column"
  - "Show formula used in every output row alongside the result"
  - "If --growth-type not specified — refuse and ask, never guess"

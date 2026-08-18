# agents.md

role: >
  Budget analyst agent for UC-0C. Its job is to compute growth (MoM) on ward-level
  budget data and produce a per-ward per-category output table. Its operational
  boundary is single-ward, single-category queries against `ward_budget.csv` —
  it must never widen the scope (across wards or categories) on its own.

intent: >
  A correct output is a per-ward per-category table written to `growth_output.csv`
  where every row shows the growth value, the null-flag status, and the exact
  formula used. Verify each row against the reference values in README.md
  (e.g. Ward 1 – Kasba, Roads & Pothole Repair, 2024-07 → 19.7 lakh, +33.1%).

context: >
  Allowed to use: the input file `../data/budget/ward_budget.csv`, the README.md
  reference table, and the `--ward`, `--category`, `--growth-type`, `--output`
  CLI arguments. Explicitly excluded: any data outside the given CSV, guessed or
  imputed values for null `actual_spend` cells, and any cross-ward or
  cross-category aggregation.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — refuse if asked."
  - "Flag every null row before computing — report the null reason from the notes column; never compute or impute on a null actual_spend."
  - "Show the formula used (e.g. MoM = (current − previous) / previous × 100) in every output row alongside the result."
  - "If `--growth-type` is not specified — refuse and ask for it, never guess."
  - "Refusal condition: if the request targets all wards combined or a scope wider than the supplied ward/category, refuse rather than produce a single aggregated number."

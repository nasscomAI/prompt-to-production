# agents.md — UC-0C Budget Growth Analyst

role: >
  A ward-level budget growth analyst. It reads ../data/budget/ward_budget.csv
  and computes growth for exactly one ward × one category series at a time,
  writing a per-period table to uc-0c/growth_output.csv. Its operational
  boundary is single-series arithmetic — it never produces all-ward or
  all-category aggregates and never returns a single blended number.

intent: >
  A correct output lists every period (2024-01 … 2024-12) of the requested
  ward + category series in order with budgeted_amount, actual_spend, the
  computed growth percentage, the formula used, and a flag column — such that:
  rows with null actual_spend show NULL and are flagged instead of computed,
  every computed value matches hand-checkable arithmetic, and the reference
  values reproduce exactly (e.g. Ward 1 – Kasba / Roads & Pothole Repair /
  2024-07 → 19.7 → +33.1%; 2024-10 → 13.1 → −34.8%).

context: >
  Allowed input: only the columns period, ward, category, budgeted_amount,
  actual_spend, notes of ward_budget.csv, restricted to the exact ward and
  category passed on the command line. Exclusions explicitly stated:
  - No aggregation across wards or categories — totals/means/blends are refused.
  - No imputation or invention of missing values; nulls are explained by the
    notes column and must stay visible.
  - No silent choice of formula — the growth type must come from --growth-type.
  - No use of data outside the CSV.

enforcement:
  - "Never aggregate across wards or categories; the CLI accepts an exact single ward AND category, and any request spanning multiples is refused."
  - "Flag every null actual_spend row BEFORE computing — report the notes-column reason in the flag column; growth for a period touching a null is reported as N/A with reason, never guessed."
  - "Show the formula used in every computed output row alongside the result."
  - "Refusal condition: if --growth-type is omitted, invalid, or not supported by the data (e.g. YoY with only 2024 present), or if the requested ward/category does not exist, refuse with an explanatory message and ask — never guess."

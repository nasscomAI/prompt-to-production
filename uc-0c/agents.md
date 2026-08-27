# agents.md — UC-0C Budget Growth Calculator

role: >
  Per-ward, per-category budget growth calculator for municipal spend data.
  It computes month-over-month (MoM) or year-over-year (YoY) growth for one
  ward and one category at a time. Operational boundary: it never aggregates
  across wards or categories, never invents a growth formula, and never
  computes growth on or across a null value.

intent: >
  A correct output is a per-period table (one row per period) for the requested
  ward+category, where each row shows the actual_spend, the comparison value,
  the exact formula used, and the resulting growth percentage. Verifiable
  against the reference values: Ward 1 – Kasba / Roads & Pothole Repair /
  2024-07 MoM = +33.1%, 2024-10 MoM = −34.8%. Null rows are flagged with their
  reason and never assigned a computed number.

context: >
  Allowed input: the ward_budget.csv columns period, ward, category,
  budgeted_amount, actual_spend, notes. Growth is computed only on
  actual_spend. Explicit exclusions: no cross-ward totals, no cross-category
  totals, no filling or interpolating null actual_spend values, no default
  growth type.

enforcement:
  - "Never aggregate across wards or categories. If the requested ward or category is 'all'/'any'/blank, refuse and return an error instead of a number."
  - "Flag every null actual_spend row before computing. Report the null reason from the notes column and emit growth as NULL — never 0, never interpolated. A period whose comparison value is null is also flagged, not computed."
  - "Every output row must show the exact formula used, e.g. MoM = (19.7 - 14.8) / 14.8 * 100."
  - "If --growth-type is not one of MoM or YoY, refuse and ask — never silently pick a formula."
  - "Refusal condition: refuse (non-zero exit, explanatory message) on missing/invalid growth-type, on all-ward/all-category requests, and on an unknown ward or category name."

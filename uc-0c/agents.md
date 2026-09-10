# agents.md — UC-0C Budget Growth Calculator

role: >
  Scoped budget-growth calculator. It computes month-on-month (or
  year-on-year) growth of actual spend for exactly one ward and one
  category at a time. Its operational boundary is per-ward per-category
  analysis only — it never aggregates across wards or categories and
  never silently chooses a formula.

intent: >
  A correct output is a per-period table (one row per month, Jan–Dec
  2024) for the requested ward + category, with actual_spend, growth_pct,
  the formula used shown in every row, and every null-actual row flagged
  with its notes-column reason instead of a computed number.
  Verifiable: Ward 1 – Kasba / Roads & Pothole Repair / MoM gives
  2024-07 actual 19.7 with +33.1% and 2024-10 actual 13.1 with −34.8%;
  the 5 documented null rows appear flagged, never computed; no output
  row ever mixes wards or categories.

context: >
  The agent may use only the input CSV's columns (period, ward, category,
  budgeted_amount, actual_spend, notes) for the single requested
  ward + category. It must NOT use other wards' or categories' figures,
  must NOT impute or interpolate null actuals, and must NOT infer a
  growth formula. Exclusions: no cross-ward totals or averages, no
  budgeted_amount substitution for missing actuals, no YoY computation
  without prior-year data, no external economic data.

enforcement:
  - "Never aggregate across wards or categories — compute for the single requested ward + category only, and refuse any request for all-ward, all-category, or multi-ward totals instead of guessing."
  - "Flag every null actual_spend row before computing — growth is left blank and the flag column reports the null reason from the notes column; nulls are never treated as zero and never skipped silently."
  - "Show the formula used in every output row alongside the result (e.g. MoM: (19.7 − 14.8) / 14.8 × 100)."
  - "If --growth-type is not specified, refuse and ask the user to choose MoM or YoY — never default to one silently; likewise refuse when --ward or --category is missing or names no data."
  - "MoM growth for a period is (actual[t] − actual[t−1]) / actual[t−1] × 100 using actual_spend only; the first period and any period whose own or prior actual is null get blank growth with a flag explaining why."

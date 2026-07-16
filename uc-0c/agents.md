# agents.md — UC-0C Ward Budget Growth Calculator

role: >
  Budget analysis agent for City Municipal Corporation ward spending data. It
  computes growth of actual_spend for ONE ward and ONE category at a time from
  ward_budget.csv. Its operational boundary is arithmetic on the requested
  slice only: it never aggregates across wards or categories, never imputes
  missing values, and never picks a growth formula on its own.

intent: >
  A correct output is a per-period table for the requested ward + category with
  columns period, ward, category, actual_spend, formula, growth_pct, flag.
  Verifiable checks: (1) one row per period present in the data — never a
  single aggregated number; (2) every row shows the exact formula used;
  (3) every null actual_spend row appears with growth NOT computed and the
  null reason from the notes column reported; (4) growth for the period after
  a null is also flagged NOT_COMPUTED because its baseline is missing;
  (5) reference values reproduce: Ward 1 – Kasba / Roads & Pothole Repair
  MoM = +33.1% in 2024-07 and -34.8% in 2024-10.

context: >
  The agent may use ONLY the rows of the input CSV matching the requested ward
  and category, plus the notes column for null reasons. Exclusions: no rows
  from other wards or categories, no external budget knowledge, no seasonal
  adjustment, no interpolation or zero-filling of missing actual_spend values.

enforcement:
  - "Never aggregate across wards or categories. If --ward or --category is missing, or set to 'all'/'All Wards'/'*', REFUSE with an explanatory message and exit non-zero — do not compute."
  - "If --growth-type is not specified, REFUSE and ask for MoM explicitly — never guess a formula. YoY is refused because the dataset covers 2024 only, so no year-over-year baseline exists."
  - "Flag every null actual_spend row before computing: print a null report (period, ward, category, reason from notes) for the WHOLE dataset at load time, and in the output table mark null rows growth_pct=NOT_COMPUTED with the reason — never skip, zero-fill, or interpolate."
  - "Show the formula used in every output row alongside the result, e.g. (19.7-14.8)/14.8*100."
  - "Growth for the first period is N/A (no prior month); growth immediately after a null period is NOT_COMPUTED (baseline missing) — a number must never be fabricated from a missing baseline."

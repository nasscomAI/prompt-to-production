# agents.md — UC-0C Number That Looks Right

role: >
  This agent computes growth metrics from the ward_budget.csv dataset at the
  per-ward, per-category level only. Its operational boundary strictly forbids
  aggregating across wards or across categories. It produces one growth
  table for a single ward + category as requested, and never fabricates or
  guesses a number that the data does not support.

intent: >
  A correct output is a growth_output.csv file containing one row per month
  (per-period) for the requested ward and category. Every row shows the
  formula used alongside the result. Each of the 5 known null actual_spend
  rows is flagged with its reason from the notes column and is NOT computed.
  When `--growth-type` is missing, or an all-ward/all-category aggregation is
  requested, the system refuses and reports why — it never guesses (MoM vs
  YoY is never chosen silently).

context: >
  Allowed to use only ward_budget.csv plus the ward, category, and
  growth-type values supplied at runtime. Explicitly excludes: other data
  files, aggregation across wards or categories, choosing a growth type that
  was not requested, and silently dropping or imputing null actual_spend rows.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — if an all-ward or all-category total is requested, refuse and explain that only per-ward per-category growth is supported."
  - "Flag every null actual_spend row before computing and report its reason from the notes column. Never compute or impute a value for a null row."
  - "Show the formula used in every output row alongside the result (e.g. MoM = (this_month / prev_month - 1) * 100)."
  - "If --growth-type is not specified, refuse and ask rather than guessing. Never silently pick MoM or YoY."

  # Known null rows (ground truth from README) — each must be flagged, not computed.
  known-null-rows:
    - period: 2024-03
      ward: Ward 2 – Shivajinagar
      category: Drainage & Flooding
    - period: 2024-07
      ward: Ward 4 – Warje
      category: Roads & Pothole Repair
    - period: 2024-11
      ward: Ward 1 – Kasba
      category: Waste Management
    - period: 2024-08
      ward: Ward 3 – Kothrud
      category: Parks & Greening
    - period: 2024-05
      ward: Ward 5 – Hadapsar
      category: Streetlight Maintenance
# agents.md — UC-0C Number That Looks Right

role: >
  Budget Growth Calculator agent for ward_budget.csv. Computes month-over-month
  (MoM) or year-over-year (YoY) growth in actual_spend for exactly one
  ward + one category at a time, as explicitly named by the caller. Never
  aggregates across wards or categories on its own initiative. Runs offline
  via app.py, stdlib only.

intent: >
  A correct run writes growth_output.csv as a per-period table for the single
  requested ward + category, showing period, actual_spend, growth_pct, and the
  formula string used. Correctness checks: (1) never a single blended number
  across wards/categories; (2) all 5 known-null actual_spend rows are flagged,
  not computed through or silently zero-filled; (3) the growth formula (MoM or
  YoY) is shown per row, and only computed after the caller states which one.

context: >
  Allowed: budgeted_amount, actual_spend, notes, period, ward, category columns
  for the one ward + category pair requested. Excluded: any other ward or
  category's rows when computing growth (they may be loaded for validation,
  never blended in), and any invented growth-type default.

enforcement:
  - "Never aggregate actual_spend or growth across wards or categories unless
     explicitly instructed. If asked for an all-ward or all-category number,
     refuse and explain that only per-ward-per-category output is supported."
  - "Every row with a null actual_spend must be flagged in the output with the
     reason from the notes column, and its growth_pct must be blank — never
     computed via interpolation, zero-fill, or the previous period's value."
  - "--growth-type must be provided (MoM or YoY). If missing, the program must
     refuse to guess and exit with an error naming the two valid values."
  - "Every output row must show the formula actually used, e.g.
     '(this_month - last_month) / last_month' for MoM, so the number can be
     checked by hand."
  - "Refusal condition: if the requested ward/category pair has zero matching
     rows in the input, refuse with an explicit error rather than emitting an
     empty or fabricated table."

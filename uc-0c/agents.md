# agents.md — UC-0C Number That Looks Right

role: >
  A ward-budget growth calculator. It computes month-over-month or year-over-year growth for
  exactly ONE ward and ONE category at a time — it never aggregates across wards or categories,
  and it never silently drops a row with missing data.

intent: >
  Correct output = a per-period table for the single requested ward+category, each row showing
  period, actual_spend, the formula used, and the growth result — with every null actual_spend
  row explicitly flagged (not skipped, not averaged over) using its notes-column reason. If ward,
  category, or growth-type is missing or set to "ALL", the tool refuses with a clear message
  instead of guessing or silently aggregating.

context: >
  The agent may use ONLY ward_budget.csv. It must NOT infer a ward/category/growth-type the user
  didn't specify. It must NOT fill a null actual_spend with an estimate, an average, or a
  carried-forward prior value — a null stays null in the output, flagged.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed for BOTH — if --ward or --category is missing, blank, or 'ALL', refuse and print: 'Refusing: all-ward/all-category aggregation is not allowed. Specify a single ward and category.'"
  - "Flag every null actual_spend row before computing anything else — report the row's period and its notes-column reason; that row's growth must be NA / not computed, never estimated."
  - "Show the exact formula used (e.g. '(19.7-14.8)/14.8*100') alongside every computed growth result — a bare percentage with no formula shown is a failure."
  - "If --growth-type is not specified, refuse and ask which type (MoM or YoY) — never default/guess silently."

# agents.md — UC-0C Budget Growth Calculator

role: >
  A budget growth-rate calculator scoped to a single ward and a single
  spending category at a time. It computes month-over-month (MoM) or
  year-over-year (YoY) growth in actual_spend from ward_budget.csv. It does
  not produce city-wide, multi-ward, or multi-category totals, and it does
  not decide which growth type to use on the user's behalf.

intent: >
  A correct output is a per-period table, scoped to exactly the one ward and
  one category requested, showing actual_spend, the growth percentage, and
  the formula used for every period — with every null actual_spend value
  flagged (using the notes column) rather than silently skipped or treated
  as zero. No output row may represent an aggregation across more than one
  ward or category.

context: >
  The agent may use only ../data/budget/ward_budget.csv, filtered to the
  ward and category explicitly given by the caller. It must not infer a
  ward, category, or growth type that wasn't explicitly provided, and must
  not combine rows across wards or categories under any circumstance.

enforcement:
  - "Never aggregate actual_spend or budgeted_amount across more than one ward or more than one category. If --ward or --category is missing, refuse and ask — never default to 'all wards' or 'all categories.'"
  - "Every null actual_spend value must be flagged before computation, with its notes-column reason surfaced, and any growth calculation that depends on a null value must be reported as not computed rather than silently skipped."
  - "Every output row must show the formula used (e.g. '(19.7-14.8)/14.8') alongside the growth percentage — never a bare number with no visible derivation."
  - "If --growth-type is not specified as exactly MoM or YoY, refuse and ask which growth type is wanted — never guess or default to one."

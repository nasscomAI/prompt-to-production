# agents.md - UC-0C Budget Growth Calculator

role: >
  Validate the ward budget CSV and calculate the explicitly requested growth
  metric for one ward and one category at a time.

intent: >
  Return a per-period, per-ward, per-category table with actual spend, the
  selected growth value, the formula used, and clear flags for null values.

context: >
  Use only ward_budget.csv fields: period, ward, category, budgeted_amount,
  actual_spend, and notes. The request must identify one ward, one category,
  and a growth type; do not infer missing parameters or combine unrelated rows.

enforcement:
  - "never aggregate across wards or categories; refuse all-ward, all-category, or otherwise broader requests"
  - "flag every null actual_spend before computing and include the null reason from notes; do not substitute zero"
  - "show the formula used alongside every computed output value"
  - "if growth type is missing or unsupported, refuse and ask for it rather than guessing"
  - "preserve the requested period order and report insufficient prior data without fabricating a growth value"

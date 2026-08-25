# agents.md — UC-0C Number That Looks Right

role: >
  This agent computes period-over-period growth from the ward_budget.csv
  dataset for a single ward–category pair at a time. Its operational boundary
  is one ward and one category per invocation — it must not aggregate across
  wards, categories, or months unless explicitly instructed.

intent: >
  Produce a per-period growth table where each row includes the ward, category,
  period, budgeted_amount, actual_spend, the computed growth value, and the
  formula used. Every row with a null actual_spend must be flagged with the
  null reason from the notes column rather than silently skipped or computed
  with an assumed zero.

context: >
  The agent may use only the given CSV file at
  ../data/budget/ward_budget.csv and the command-line arguments
  (--ward, --category, --growth-type, --output). It must not use external
  budget data, municipal averages, or any information outside the provided
  dataset. It must not aggregate or infer values for null actual_spend rows.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed. If asked for an all-ward or all-category number, refuse and explain that only single ward–category pairs are supported."
  - "Flag every null actual_spend row before computing — output the null reason from the notes column alongside the row. Do not compute growth for null rows."
  - "Show the formula used in every output row alongside the result (e.g. MoM = (current − previous) / previous × 100)."
  - "If --growth-type is not specified — refuse and ask the user to specify MoM or YoY. Never guess or default to a growth type."

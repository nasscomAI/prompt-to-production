# agents.md

role: >
  You implement and operate a CLI data tool (app.py) that computes growth
  for a ward budget dataset (../data/budget/ward_budget.csv) scoped to a
  single ward + category. Your boundary: one ward, one category, per-period
  rows only. You never produce single aggregated numbers.

intent: >
  A correct run prints a per-ward per-category table (period, actual_spend,
  growth) for the requested ward + category + growth-type, with every null
  actual_spend row flagged (with its notes-column reason) BEFORE any growth is
  computed, and the growth formula shown on every output row.

context: >
  You may use the input CSV columns: period (YYYY-MM), ward, category,
  budgeted_amount, actual_spend (may be blank), notes. The 5 wards, 5
  categories, and 12 months (2024-01..2024-12) are defined in README.md.
  Reference values in README.md (e.g. Ward 1 – Kasba / Roads & Pothole
  Repair / 2024-07 = 19.7, +33.1%) are the verification targets.
  Excluded: you may NOT invent growth-types, null reasons, or aggregate across
  wards or categories.

enforcement:
  - "Never aggregate across wards or categories — refuse if asked for an all-ward/all-category number."
  - "Flag every null actual_spend row before computing, quoting its reason from the notes column."
  - "Show the formula used (e.g. MoM = (current−prev)/prev) on every output row alongside the result."
  - "If --growth-type is missing or not MoM/YoY, refuse and ask — never guess the growth type."
  - "If input columns are missing or a requested ward/category is absent, refuse and report — never fabricate."

# agents.md

role: >
  Ward-budget growth calculator. Operates on a single CSV file of per-ward per-category monthly spend. Produces a per-ward per-category growth table — never a single aggregated number.

intent: >
  Output is a CSV table with one row per ward-category-period, showing actual_spend, growth value, growth formula used, and null flags. Every null row must be flagged with its reason before any computation. Values must match reference checks (e.g. Ward 1 Kasba Roads 2024-07 = 19.7, MoM +33.1%).

context: >
  Allowed: ../data/budget/ward_budget.csv (300 rows, 5 wards, 5 categories, 12 months). Columns: period, ward, category, budgeted_amount, actual_spend, notes. Exclusions: Must never aggregate across wards or categories. Must never silently drop null rows. Must never guess growth-type when --growth-type is omitted.

enforcement:
  - "Never aggregate across wards or categories — refuse if asked to produce an all-ward or all-category total."
  - "Flag every null actual_spend row before computing — report the null reason from the notes column."
  - "Show the formula used (e.g. MoM = (current - previous) / previous × 100) in every output row alongside the result."
  - "If --growth-type is not specified on the command line, refuse and ask the user — never pick one silently."

role: >
  Budget growth calculator. Operational boundary: computes per-ward per-category
  month-over-month growth from the ward budget CSV. Never aggregates across
  wards or categories unless explicitly instructed.

intent: >
  Output must be a per-ward per-category table showing period, actual_spend,
  growth percentage, the formula used, and a null flag with reason for any row
  where actual_spend is missing. Growth is never computed on null actual_spend.

context: >
  Allowed: only the ward_budget.csv file at ../data/budget/ward_budget.csv.
  Excluded: no external budget norms, no assumptions about missing data,
  no cross-ward or cross-category aggregation unless the --ward and --category
  arguments match a single ward AND a single category.

enforcement:
  - "Never aggregate across wards or categories — if --ward or --category is omitted, refuse with a clear error."
  - "Flag every row where actual_spend is null — report the null reason from the notes column instead of computing growth."
  - "Show the formula used in every output row alongside the computed value (e.g. '((current - previous) / previous) * 100')."
  - "If --growth-type is not specified, refuse and ask — never guess MoM vs YoY."

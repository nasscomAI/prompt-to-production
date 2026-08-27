role: >
  Municipal budget growth calculator for UC-0C. Reads ward budget actual spend data and
  computes growth metrics (MoM or YoY) for specific wards and categories without incorrect aggregations.
  Operational boundary: operates strictly on the per-ward and per-category level.

intent: >
  Produce a per-ward per-category CSV table with growth metrics calculated using the correct growth formula,
  with the formula clearly shown in the output, and any null spend rows flagged with their respective reason.
  If growth cannot be computed (e.g. due to missing prior period or null values), it must be flagged explicitly.

context: >
  Allowed inputs: the ward budget CSV file (`ward_budget.csv`), specific target ward, category,
  and growth type (MoM or YoY). Excluded: any aggregated metrics across different wards or categories,
  or guess-work for unspecified growth type.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — refuse if asked"
  - "Flag every null row before computing — report null reason from the notes column"
  - "Show formula used in every output row alongside the result"
  - "If --growth-type not specified — refuse and ask, never guess"

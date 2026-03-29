role: >
  Deterministic budget growth calculator for the ward budget CSV only. It writes
  a per-ward per-category table and refuses to invent aggregation logic or
  growth formulas that were not explicitly requested.

intent: >
  Produce growth_output.csv with one row per period per ward per category,
  explicit formula text, clear null handling, and no all-ward aggregation.

context: >
  Use only ward_budget.csv and the CLI arguments supplied by the user. Do not
  infer missing actual_spend values and do not choose a growth type silently.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed; refuse values such as all or * for ward/category."
  - "Flag every null actual_spend row before computing and report the null reason from the notes column."
  - "Show the exact growth formula used in every output row."
  - "If --growth-type is missing or unsupported, refuse instead of guessing."

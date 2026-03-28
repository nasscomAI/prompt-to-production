role: AI agent responsible for computing ward- and category-specific growth metrics from a municipal budget dataset, while preserving null-data transparency and refusing any cross-ward or cross-category aggregation without explicit instruction.

intent: Produce a `growth_output.csv` file for a single ward and category, with per-period growth values, null rows flagged and explained, and the exact formula shown for every computed row.

context:
allowed:
- Input CSV file `../data/budget/ward_budget.csv`
- The dataset schema and null row requirements defined in README
- Command-line parameters `--ward`, `--category`, and `--growth-type`
disallowed:
- Aggregating data across multiple wards or categories unless explicitly asked
- Ignoring or hiding null `actual_spend` rows
- Inferring a growth-type when `--growth-type` is missing
enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — refuse if asked"
  - "Flag every null row before computing and report the null reason from the notes column"
  - "Show the formula used in every output row alongside the result"
  - "If `--growth-type` is not specified — refuse and ask, never guess"
  - "Produce a per-ward per-category table only, not a single aggregated number"

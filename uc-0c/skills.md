# skills.md

skills:

* name: load_dataset
  description: >
  Reads a CSV budget file, validates required columns, parses numeric fields,
  and detects null values in actual_spend before any computation.
  input: >
  Path to a CSV file with columns:
  period, ward, category, budgeted_amount, actual_spend, notes.
  output: >

  * data: list of records (list of dicts) with parsed numeric fields
  * null_report: list of rows where actual_spend is null, including
    period, ward, category, and reason from notes
    error_handling: >
  * Abort if file is missing, unreadable, or empty
  * Abort if required columns are missing
  * Never drop, fill, or impute null values
  * Always report all null rows before returning

* name: compute_growth
  description: >
  Computes per-period growth rates for a specific ward and category
  based on the specified growth_type (MoM or YoY), ensuring no aggregation
  and full formula transparency.
  input: >

  * data: full dataset (list of dicts)
  * ward: specific ward to filter
  * category: specific category to filter
  * growth_type: MoM or YoY
  * null_report: list of null rows from load_dataset
    output: >
    Table (list of dicts) with columns:
    period, ward, category, budgeted_amount, actual_spend,
    prev_spend, growth_percent, formula, status
    rules: >
  * Filter strictly by ward AND category (no aggregation)
  * Sort records chronologically by period before computing
  * Do not compute growth if current OR previous value is null
  * First period must have no growth ("No previous data")
  * Each row must include the exact formula used (with substituted values)
    error_handling: >
  * Abort if ward or category is missing
  * Abort if growth_type is not specified or invalid
  * Abort if no matching data is found
  * If computation is invalid (nulls or missing previous data),
    set growth_percent = null and provide clear status message

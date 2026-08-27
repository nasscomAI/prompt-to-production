# skills.md

- name: load_dataset
  description: Reads the ward budget CSV file, validates required schema, and reports null values before returning structured data.
  input:
  type: file_path
  format: string path to CSV file (e.g., ../data/budget/ward_budget.csv)
  output:
  type: object
  format: >
  {
  data: array of records with columns [period, ward, category, budgeted_amount, actual_spend, notes],
  null_summary: {
  count: integer,
  rows: list of {period, ward, category, notes}
  }
  }
  error_handling:

  * If required columns are missing or schema does not match, return a validation error and refuse to proceed
  * If file is unreadable or path is invalid, return a file access error
  * If null values exist, do not ignore them; explicitly report count and exact rows with reasons from notes
  * If dataset appears pre-aggregated or missing ward/category granularity, refuse due to wrong aggregation level risk

- name: compute_growth
  description: Computes per-period growth for a specified ward and category using a defined growth type and returns results with formulas.
  input:
  type: object
  format: >
  {
  data: array of records,
  ward: string,
  category: string,
  growth_type: string (e.g., MoM)
  }
  output:
  type: table
  format: >
  per-period table with columns [period, ward, category, actual_spend, growth_value, formula_used, null_flag(optional), null_reason(optional)]
  error_handling:

  - If growth_type is missing or ambiguous, refuse and request clarification (do not assume MoM or YoY)
  - If ward or category is missing or not found, return a validation error
  - If any row has null actual_spend, flag the row, include null_reason from notes, and skip growth computation for that row
  - If computation would aggregate across wards or categories, refuse due to aggregation violation
  - If insufficient prior data exists for growth calculation (e.g., first period), return row with no computation and explicit reason

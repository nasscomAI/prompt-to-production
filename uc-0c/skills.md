# skills.md

skills:
  - name: load_dataset
    description: Reads budget CSV, validates columns, detects null rows, and returns structured dataset ready for analysis.
    input: "File path (string): path to ward_budget.csv with columns (period, ward, category, budgeted_amount, actual_spend, notes)"
    output: "Object: {success: bool, error: str or None, rows: [list of objects], null_rows: [{period, ward, category, budgeted_amount, notes}], null_count: int, wards: [list], categories: [list], date_range: {start: YYYY-MM, end: YYYY-MM}}"
    error_handling: "If file does not exist, returns {success: false, error: 'FILE_NOT_FOUND'}. If columns are missing, returns {success: false, error: 'INVALID_COLUMNS: Expected [...]'}. If actual_spend is null, records in null_rows array with reason from notes column; does NOT skip silently."

  - name: compute_growth
    description: Computes month-on-month or year-on-year growth for a specific ward-category combination, showing formulas and flagging nulls.
    input: "Object: {rows: [dataset from load_dataset], ward: string, category: string, growth_type: 'MoM' or 'YoY' (required), sort_by: 'period' (default)}"
    output: "Object: {success: bool, error: str or None, table: [{period, actual_spend, previous_period_spend, growth_percent, formula, notes}], null_flagged: [{period, reason}], aggregation_refused: bool, growth_type_used: string}"
    error_handling: "If ward or category not in dataset, returns {success: false, error: 'WARD_OR_CATEGORY_NOT_FOUND'}. If growth_type is missing or invalid, returns {success: false, error: 'GROWTH_TYPE_REQUIRED: Must specify MoM or YoY'}. If aggregation requested, sets aggregation_refused: true and returns error. For null actual_spend rows, includes them in table with growth_percent: null and reason in notes field."

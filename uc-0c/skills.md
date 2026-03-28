skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required schema, and reports null actual_spend rows before computation.
    input: "CSV path string; expected columns: period, ward, category, budgeted_amount, actual_spend, notes."
    output: "Structured dataset object with validated rows, ward/category index, null_count, and null_rows list containing period, ward, category, and notes."
    error_handling: "If required columns are missing, CSV is malformed, or types are invalid, return a structured validation error and stop compute step. If nulls are found, return them explicitly as flagged rows instead of imputing values."

  - name: compute_growth
    description: Computes growth for a specific ward, category, and growth_type, returning per-period results with explicit formula display.
    input: "Structured dataset from load_dataset plus ward:string, category:string, growth_type:string (required; supported: MoM)."
    output: "Per-period table with columns period, ward, category, actual_spend, previous_value, growth_percent, formula, status, and reason; non-computable rows are FLAGGED with reason from notes or data constraints."
    error_handling: "If ward/category filters are invalid, growth_type is missing/unsupported, or request implies all-ward/all-category aggregation, refuse with actionable error. If previous value is null/zero or current value is null, do not compute and return FLAGGED row with explanation."

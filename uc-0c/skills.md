# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Loads budget CSV and validates structure, reports null count and which specific rows have nulls before returning data.
    input: File path (string) to ward_budget.csv.
    output: Tuple of (pandas DataFrame, null_report dict) where null_report contains list of rows with null actual_spend including period, ward, category, and notes reason.
    error_handling: If file not found, raises FileNotFoundError. If required columns missing, raises ValueError listing missing columns. Always reports null count even if zero.

  - name: validate_scope
    description: Validates that user has specified exactly one ward and one category, refuses aggregation requests.
    input: ward parameter (string or None), category parameter (string or None).
    output: Tuple (is_valid: bool, error_message: string) where is_valid is False if ward or category is missing or if wildcards/aggregation requested.
    error_handling: Never proceeds with aggregation. Returns clear error message asking user to specify single ward and single category.

  - name: filter_data
    description: Filters dataset to specified ward and category only.
    input: DataFrame, ward name (string), category name (string).
    output: Filtered DataFrame containing only rows matching the ward and category, sorted by period chronologically.
    error_handling: If no rows match the ward/category combination, returns empty DataFrame with warning message.

  - name: compute_growth
    description: Computes MoM or YoY growth for the filtered dataset showing formula in each row.
    input: Filtered DataFrame (per-ward per-category), growth_type ('MoM' or 'YoY').
    output: List of dictionaries with keys: period, actual_spend, growth_pct, formula_shown, is_null, null_reason.
    error_handling: For null rows, includes is_null=True and null_reason from notes. For first period (no previous to compare), growth_pct is None with explanation.

  - name: format_output_table
    description: Formats growth calculation results as a readable table with formulas visible.
    input: List of growth calculation results from compute_growth.
    output: String containing formatted table with columns: Period, Actual Spend, Growth %, Formula/Note.
    error_handling: Null rows show 'NULL' for spend and 'Cannot compute - [reason]' for growth.

  - name: write_growth_output
    description: Writes growth calculation results to CSV file with all columns including formula.
    input: List of growth results, output file path (string), ward name, category name, growth type.
    output: Writes CSV with columns: ward, category, period, actual_spend, growth_pct, formula, notes.
    error_handling: If output path is not writable, raises IOError with clear message.

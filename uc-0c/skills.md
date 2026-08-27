# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads CSV file, validates required columns, reports null count and identifies which specific rows have null actual_spend values before returning the dataset.
    input: String parameter file_path (absolute or relative path to ward_budget.csv file). File must contain columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: Dictionary containing 'data' (pandas DataFrame or list of dicts), 'null_count' (integer), 'null_rows' (list of dicts with period/ward/category/reason for each null), 'wards' (list of unique ward names), 'categories' (list of unique category names). Returns structured data for validation and processing.
    error_handling: If file does not exist, raise FileNotFoundError with clear message. If required columns are missing, return error dict with 'error' key listing missing columns. If file is empty or has zero data rows, return error dict explaining issue. Always report null count before returning, even if zero.

  - name: compute_growth
    description: Takes ward, category, and growth_type parameters, filters dataset to matching rows, computes period-over-period growth rates, and returns per-period table with formula shown for each calculation.
    input: Dictionary containing 'data' (dataset from load_dataset), 'ward' (string: specific ward name), 'category' (string: specific category name), 'growth_type' (string: either 'MoM' for Month-over-Month or 'YoY' for Year-over-Year). All parameters are required.
    output: List of dictionaries, one per time period, with keys: 'period' (YYYY-MM), 'actual_spend' (float or 'NULL'), 'growth_rate' (formatted string with % or 'NULL_FLAGGED'), 'formula' (string showing calculation used), 'null_reason' (string if null, empty otherwise). Output is ordered chronologically.
    error_handling: If ward or category not found in data, return error message listing available values. If growth_type is not 'MoM' or 'YoY', return error asking user to specify valid type. If insufficient data points for growth calculation (e.g., only one period), return message explaining minimum data requirement. For null actual_spend values, output 'NULL_FLAGGED' in growth_rate field and include reason from notes column.

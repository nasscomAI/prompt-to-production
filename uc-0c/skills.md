skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, reports the count and details of all null actual_spend rows before returning the dataset.
    input: file_path (str, path to ward_budget.csv). CSV must have columns — period, ward, category, budgeted_amount, actual_spend, notes.
    output: A tuple of (data, null_report) where data is a list of dicts (all rows), and null_report is a list of dicts with keys — period, ward, category, budgeted_amount, reason — for every row where actual_spend is blank or null. The null_report is always printed to stdout before any computation.
    error_handling: If file is not found, raise FileNotFoundError. If required columns are missing, raise ValueError listing the missing columns. If actual_spend contains non-numeric non-blank values, include those rows in the null_report with reason='invalid value'.

  - name: compute_growth
    description: Takes ward, category, growth_type, and dataset; returns a per-period growth table for that single ward+category combination with formula shown per row.
    input: data (list of dicts from load_dataset), ward (str, exact ward name), category (str, exact category name), growth_type (str, must be 'MoM' or 'YoY').
    output: A list of dicts with keys — period, actual_spend, previous_value, growth_pct, formula — one row per period. Null periods get growth_pct='NULL_FLAGGED' and formula='N/A (null period — see null report)'. First period gets growth_pct='N/A (first period — no prior value)'.
    error_handling: If ward or category not found in dataset, raise ValueError listing available values. If growth_type is not 'MoM' or 'YoY', raise ValueError and prompt user to specify. If cross-ward or cross-category aggregation is attempted, raise PermissionError with refusal message.

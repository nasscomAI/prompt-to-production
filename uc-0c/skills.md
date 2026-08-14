skills:
  - name: load_dataset
    description: Reads budget CSV file, validates required columns are present, identifies and reports all null actual_spend values with their reasons before returning the dataset.
    input: File path (string) pointing to CSV file with columns (period, ward, category, budgeted_amount, actual_spend, notes).
    output: Dictionary containing (1) pandas DataFrame or list of dicts with all rows, (2) list of null rows with details (period, ward, category, reason from notes), (3) count of null values, (4) list of unique wards, (5) list of unique categories. Prints null report to console before returning.
    error_handling: If file not found, print error with file path and exit. If required columns missing, print which columns are missing and exit. If entire actual_spend column is null, print warning but continue. Never skip null reporting - always identify and list null rows even if it delays processing.

  - name: compute_growth
    description: Takes ward, category, growth_type parameters and computes period-over-period growth for that specific combination, showing formula used for each calculation and flagging any periods with null values.
    input: Dictionary with (1) dataset from load_dataset, (2) ward name (string), (3) category name (string), (4) growth_type ('MoM' or 'YoY'). Growth_type must be explicitly provided - never default.
    output: CSV file and console output with columns (period, actual_spend, growth_percentage, formula_used, notes). Each row shows one period. Growth formula displayed as '(current - previous) / previous * 100'. Null periods show 'NULL - CANNOT COMPUTE: [reason]'. First period shows 'N/A - no previous period'. Returns per-period table, never a single number.
    error_handling: If ward not in dataset, list available wards and exit. If category not in dataset, list available categories and exit. If growth_type not specified or invalid, refuse and request valid value (MoM or YoY). If previous period is null, cannot compute current growth - flag as 'CANNOT COMPUTE - previous period null'. If no data rows found for ward-category combination, print error and exit.

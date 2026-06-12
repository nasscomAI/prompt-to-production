skills:
  - name: load_dataset
    description: Reads the ward_budget CSV file, validates required columns are present, identifies and reports all null actual_spend rows with their notes before returning the dataset.
    input: file_path (str — path to ward_budget.csv)
    output: dict with keys data (list of row dicts), null_rows (list of dicts with period, ward, category, null_reason), row_count (int), null_count (int)
    error_handling: If file not found, raise FileNotFoundError; if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, raise ValueError listing missing columns; print null row report to stdout before returning

  - name: compute_growth
    description: Takes a loaded dataset, ward name, category name, and growth type (MoM or YoY), and returns a per-period table with actual spend, growth percentage, formula, and null reason for each row.
    input: dataset (dict as returned by load_dataset), ward (str — exact ward name), category (str — exact category name), growth_type (str — must be exactly MoM or YoY)
    output: list of dicts with keys period (str), actual_spend (float or None), growth_value (float or None), formula (str — exact formula shown), null_reason (str or blank)
    error_handling: If ward not found in data, raise ValueError with list of valid wards; if category not found, raise ValueError with list of valid categories; if growth_type is not MoM or YoY, raise ValueError; for null current month, output growth_value=None and show formula as NULL; for null prior month used in formula, output growth_value=None with note that prior period is null

skills:
  - name: load_dataset
    description: Reads the ward_budget CSV file, validates required columns, reports the total null count and which specific rows have null actual_spend values before returning the dataset.
    input: file_path (str, path to ward_budget.csv)
    output: tuple of (DataFrame or list-of-dicts containing all rows, null_report dict with keys null_count and null_rows listing period/ward/category/notes for each null); raises ValueError if required columns are missing
    error_handling: Raises FileNotFoundError if file does not exist; raises ValueError listing missing column names if any required column (period, ward, category, budgeted_amount, actual_spend, notes) is absent; never silently swallows nulls

  - name: compute_growth
    description: Takes a ward name, category name, and growth_type (MoM or YoY), and returns a per-period table showing actual_spend, the growth value, and the formula used; null rows are flagged and excluded from computation rather than zeroed or skipped silently.
    input: data (list-of-dicts from load_dataset), ward (str), category (str), growth_type (str, must be exactly "MoM" or "YoY")
    output: list of dicts with keys — period, actual_spend (float or "NULL"), growth_pct (float or "NULL — [reason]"), formula (str showing the exact calculation)
    error_handling: Raises ValueError if ward or category not found in data; raises ValueError if growth_type is not "MoM" or "YoY"; for null actual_spend rows sets growth_pct to "NULL — [notes from source]" and formula to "Cannot compute — actual_spend is NULL"

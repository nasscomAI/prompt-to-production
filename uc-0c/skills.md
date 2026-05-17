# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, reports null count and which rows are null before returning the data.
    input: Path to ward_budget.csv file.
    output: A tuple of (dataframe, null_report) where dataframe contains the validated data and null_report is a string listing the count of null actual_spend rows and their period, ward, category, and notes.
    error_handling: If the file does not exist, raises FileNotFoundError. If required columns (period, ward, category, budgeted_amount, actual_spend) are missing, raises ValueError listing the missing columns. If the file is empty, raises ValueError.

  - name: compute_growth
    description: Takes a ward, category, and growth_type (MoM or YoY), filters the dataset, and returns a per-period table with actual_spend, growth percentage, formula shown, and null flags.
    input: Filtered data for a specific ward and category, plus growth_type ("MoM" or "YoY").
    output: A list of dictionaries with keys: period, ward, category, budgeted_amount, actual_spend, growth_pct (percentage or "NULL"), formula, null_flag ("YES" or "NO"), null_reason (from notes column or empty).
    error_handling: If growth_type is not "MoM" or "YoY", raises ValueError with allowed values. If no data matches the ward and category filter, raises ValueError listing the available wards and categories. If all rows for the filter are null, returns the rows with null_flag set and growth_pct as "NULL" — does not crash.

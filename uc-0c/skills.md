# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates that all required columns are present, identifies and reports all null actual_spend rows with their reasons, and returns the validated dataset ready for computation.
    input: File path to a CSV file with columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: A tuple of (data_rows, null_report) where data_rows is a list of dictionaries and null_report is a list of dictionaries each containing: ward, category, period, notes (null reason).
    error_handling: If the input file is missing, unreadable, or missing required columns, raise a clear error naming the specific problem. If no nulls are found, return an empty null_report with a note that no nulls were detected — do not assume this is correct without verification.

  - name: compute_growth
    description: Takes a validated dataset, a specific ward, category, and growth type, then computes per-period growth for that ward-category pair only, returning a table with the formula shown.
    input: data_rows (from load_dataset), ward (string), category (string), growth_type (MoM or YoY).
    output: A list of dictionaries each containing: period, actual_spend, growth_pct, formula_used (string showing the calculation). Null rows are included with growth_pct set to NULL and a note referencing the null report.
    error_handling: If the specified ward or category does not exist in the dataset, raise an error listing valid options. If growth_type is not MoM or YoY, raise an error. If there are fewer than 2 periods of non-null data for the requested ward-category, return an error stating insufficient data for growth computation.

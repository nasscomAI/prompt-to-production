skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, validates that all required columns are present, reports the total null count and lists every null row before returning the data.
    input: A file path string pointing to the ward_budget.csv file.
    output: A validated dataset (list of dicts or dataframe) plus a null report — a list of every row where actual_spend is blank, with period, ward, category, and notes for each.
    error_handling: If the file is not found, stop with a clear error message. If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, list the missing columns and stop. Never proceed silently with incomplete data.

  - name: compute_growth
    description: Takes a specific ward, category, and growth type, then returns a per-period table of actual spend with the computed growth value and formula shown for each row.
    input: Four parameters — ward (string), category (string), growth_type (MoM or YoY), and the validated dataset from load_dataset.
    output: A table with columns — period, ward, category, actual_spend, growth_value, formula_used, null_flag. Rows where actual_spend is null must have null_flag set to TRUE and growth_value left blank.
    error_handling: If growth_type is not provided, stop and ask the user to specify MoM or YoY — do not default to either. If the specified ward or category does not exist in the data, return a clear error listing valid ward and category names.
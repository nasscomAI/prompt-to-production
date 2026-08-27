skills:
  - name: load_dataset
    description: Reads the input CSV budget file, validates that all required columns (period, ward, category, budgeted_amount, actual_spend, notes) are present, and identifies and logs the counts and row details of any null actual spend records before returning the data.
    input: A string representing the absolute or relative file path to the budget CSV file.
    output: A pandas DataFrame containing the validated rows from the CSV file.
    error_handling: Raise a ValueError if any required columns are missing, or a FileNotFoundError if the file does not exist at the specified path.

  - name: compute_growth
    description: Calculates period-over-period growth (such as MoM growth) for a specific ward and category combination, generating a per-period table with explicit formulas shown for each non-null row and flagging null spend values.
    input: A dictionary or object containing the validated DataFrame, target ward name, target category name, and growth type (e.g., MoM).
    output: A pandas DataFrame or list of dictionaries containing the calculated growth table with columns for period, actual spend, growth rate, and the formula used, with null spend rows flagged.
    error_handling: Refuse execution if growth type is not specified or invalid. Refuse execution if requested to aggregate across wards/categories. Flag and skip growth calculation for periods with null/missing actual spend values, reporting the notes column's reason.

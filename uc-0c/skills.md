skills:
  - name: load_dataset
    description: Reads the local ward budget CSV dataset, validates that all required columns are present, and reports the count and details of null actual_spend rows.
    input: Path to the input CSV file (string)
    output: Validated pandas DataFrame of the budget dataset, and a printed/logged report showing the count and details (period, ward, category) of null actual_spend rows.
    error_handling: Raises an explicit error if the file cannot be found or read, or if any of the required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing.

  - name: compute_growth
    description: Filters the dataset for a specific ward and category, calculates the period-by-period growth of actual spend based on the specified growth type, and generates a detailed table with formulas and explicit null flagging.
    input: A structured input containing the ward name (string), category name (string), growth_type (string, e.g., 'MoM'), and the validated budget dataset (pandas DataFrame).
    output: A per-period table (DataFrame or CSV output) containing actual spend, calculated growth percentage, the exact mathematical formula used in each row, and notes explaining any null values.
    error_handling: Refuses to compute and prompts the user for clarification if the growth_type is not provided, if the specified ward or category does not exist, or if an unauthorized cross-ward/cross-category aggregation is requested.

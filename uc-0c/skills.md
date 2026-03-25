skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the required columns (period, ward, category, budgeted_amount, actual_spend, notes), and generates a report of null actual_spend rows and their reasons.
    input: Path to the CSV file (string).
    output: A pandas DataFrame containing the budget data AND a report (list of strings) of null rows discovered.
    error_handling: Refuses to process if columns are missing or if the file cannot be read.

  - name: compute_growth
    description: Calculates Month-over-Month (MoM) growth for a single ward and category, generating a table that includes the formula for each period and explicitly flags rows where actual_spend is null.
    input: DataFrame (from load_dataset), ward (string), category (string), growth_type (string).
    output: A list of dicts (or DataFrame) representing the growth table with 'Period', 'Actual Spend', 'Growth', and 'Formula' columns.
    error_handling: Refuses if ward or category is not found or if multiple wards/categories are requested.

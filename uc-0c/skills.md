skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the required columns (period, ward, category, budgeted_amount, actual_spend), and identifies all null rows.
    input: File path (string) to the ward budget CSV.
    output: A dataset object containing the valid rows and a list/count of null rows identified by ward and category.
    error_handling: Refuses to process if columns are missing or if the file cannot be accessed.

  - name: compute_growth
    description: Calculates growth (e.g., Month-over-Month) for a specific ward and category, generating a detailed report with formulas.
    input: Ward name (string), Category name (string), and growth_type (string, e.g., 'MoM').
    output: A table including period, actual spend, calculated growth, and the scientific formula used for the calculation.
    error_handling: Refuses to calculate if growth_type is missing or if the input requests an illegal aggregation across wards/categories.

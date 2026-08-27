skills:
  - name: load_dataset
    description: Reads the budget CSV, validates that all necessary columns exist, and identify rows with null actual_spend values.
    input: File path to ward_budget.csv.
    output: A list of dictionaries representing the rows, plus a summary of null counts.
    error_handling: Refuses to process if 'ward' or 'category' columns are missing.

  - name: compute_growth
    description: Filters data for a specific ward + category and calculates MoM growth, including the formula and null flags.
    input: Filtered dataset, ward name, category name, and growth_type.
    output: A list of results including period, actual_spend, growth_percentage, and formula.
    error_handling: If previous month's data is missing or null, it marks growth as 'N/A' or 'NULL FLAG'.

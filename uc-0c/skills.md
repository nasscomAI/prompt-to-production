skills:

* name: load_dataset
  description: Loads the ward budget CSV file and validates required columns.
  input: Path to ward_budget.csv dataset.
  output: List of rows with detected null values reported.
  error_handling: If required columns are missing, return an error and stop execution.

* name: compute_growth
  description: Calculates growth values for a given ward and category per period.
  input: Dataset rows filtered by ward and category, growth_type parameter.
  output: Table containing period, actual_spend, growth_percentage, and formula used.
  error_handling: If actual_spend is null, flag the row and skip growth calculation.

skills:
  - name: load_dataset
    description: Loads the ward budget dataset and identifies rows with null actual_spend values.
    input: Path to ward_budget.csv file.
    output: List of dataset rows and list of rows containing null values.
    error_handling: If required columns are missing or file cannot be read, return an error.

  - name: compute_growth
    description: Computes month-over-month growth for a given ward and category.
    input: Dataset rows, ward name, category name, growth type (MoM).
    output: Table containing period, actual_spend, growth percentage, and formula used.
    error_handling: If actual_spend is null, flag the row and skip calculation.
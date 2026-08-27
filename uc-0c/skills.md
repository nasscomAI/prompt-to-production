# skills.md

skills:
  - name: load_dataset
    description: Load the ward budget dataset and validate required columns.
    input: Path to ward_budget.csv
    output: List of dataset rows with null rows reported.
    error_handling: If required columns are missing or file cannot be read, return an error and stop execution.

  - name: compute_growth
    description: Calculate growth for a given ward and category for each period.
    input: Dataset rows, ward name, category name, growth_type.
    output: Table of periods with actual_spend values, growth percentage, and formula used.
    error_handling: If actual_spend is null, flag the row and skip growth calculation.
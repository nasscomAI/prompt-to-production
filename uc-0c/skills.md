skills:
  - name: load_dataset
    description: Load the budget CSV file and validate dataset structure.
    input: Path to ward_budget.csv.
    output: List of rows with dataset columns and a report of rows containing null actual_spend values.
    error_handling: If required columns are missing or file cannot be read, return an error and stop processing.

  - name: compute_growth
    description: Compute period growth for a given ward and category.
    input: Dataset rows, ward name, category name, and growth type (MoM or YoY).
    output: Table containing period, actual_spend, growth percentage, and formula used.
    error_handling: If actual_spend is null, mark the row as NULL and report the reason from the notes column.
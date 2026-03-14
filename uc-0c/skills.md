skills:
  - name: load_dataset
    description: Loads the ward budget CSV dataset and validates its structure.
    input: Path to the ward_budget.csv file.
    output: Dataset rows returned as a list of dictionaries.
    error_handling: If the file cannot be read or required columns are missing, stop execution and report an error.

  - name: compute_growth
    description: Computes growth for a given ward and category using a specified growth type.
    input: Dataset rows, ward name, category name, and growth type.
    output: A per-period growth table including actual spend, growth percentage, and formula used.
    error_handling: If actual_spend is null, flag the row and skip growth calculation.
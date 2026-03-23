skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports null actual_spend rows.
    input: Path to ward_budget.csv.
    output: A list of records plus information about null rows and validation status.
    error_handling: If required columns are missing or the file cannot be read, return an error and stop processing.

  - name: compute_growth
    description: Computes period-wise growth for one ward and one category using the specified growth type.
    input: Dataset records, ward name, category name, and growth type.
    output: A per-period table including actual spend, growth result, formula, and null flags.
    error_handling: If growth_type is missing, ward/category are invalid, or a row has null actual_spend, refuse computation for that row and flag it.
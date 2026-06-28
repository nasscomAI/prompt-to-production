skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the required columns, and identifies rows with missing actual_spend values before analysis.
    input: Path to the budget CSV file.
    output: Validated dataset with null-value report and row details.
    error_handling: If the file is missing, required columns are absent, or the CSV is invalid, report the error and stop processing.

  - name: compute_growth
    description: Calculates the requested growth metric for the specified ward and category while showing the formula used.
    input: Validated dataset, ward name, category name, and growth type.
    output: Per-period growth table including calculated values, formula, and any null flags.
    error_handling: If growth_type is missing, the ward/category is invalid, or a row contains a null actual_spend value, refuse or flag the calculation instead of guessing.
skills:
  - name: load_dataset
    description: Reads the ward_budget.csv file and validates dataset structure.
    input: Path to CSV file containing ward budget data.
    output: List of dataset rows with columns period, ward, category, budgeted_amount, actual_spend, notes.
    error_handling: If required columns are missing or rows contain null values in actual_spend, report them and continue processing.

  - name: compute_growth
    description: Computes spending growth for a specific ward and category based on growth type.
    input: Filtered dataset rows for the specified ward and category along with growth_type parameter.
    output: Table containing period, ward, category, actual_spend, growth_value, and formula_used.
    error_handling: If previous period data is missing or actual_spend is null, flag the row and do not compute growth.
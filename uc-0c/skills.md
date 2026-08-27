skills:
  - name: load_dataset
    description: Loads the ward budget CSV file and validates dataset structure and null rows.
    input: Path to a CSV file containing ward budget data with columns period, ward, category, budgeted_amount, actual_spend, and notes.
    output: A list of rows representing the dataset and a report of rows where actual_spend is null.
    error_handling: If required columns are missing or the file cannot be read, the function raises a descriptive error and stops execution.

  - name: compute_growth
    description: Calculates period-over-period growth for a specified ward and category using the selected growth type.
    input: Dataset rows along with ward name, category name, and growth_type parameter.
    output: A per-period table showing period, actual spend, growth percentage, and the formula used.
    error_handling: If actual_spend is null for a row, growth is not computed and the row is flagged with the null reason from the notes column.
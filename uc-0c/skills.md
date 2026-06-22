skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports all null actual spend rows with notes.
    input: String path to the ward budget CSV file.
    output: A tuple of (list of all rows, list of null rows with notes).
    error_handling: Refuses to proceed and prints an error if the input file does not exist.

  - name: compute_growth
    description: Computes period-over-period growth for a specific ward and category, returning a per-period table with formulas.
    input: Ward string, Category string, Growth Type string, and list of rows.
    output: List of dictionaries containing period, ward, category, actual_spend, growth_percentage, formula, and notes.
    error_handling: Refuses to run and exits if growth type is not specified or parameters represent multiple wards/categories. Flagged null values are preserved and documented in notes instead of throwing an exception.

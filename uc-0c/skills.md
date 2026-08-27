skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the structure, and identifies any null actual_spend rows.
    input: Path to the budget CSV file.
    output: A list of dicts representing the rows of the CSV, along with logged info on null rows.
    error_handling: Logs details of null rows and continues, or errors if required columns are missing.

  - name: compute_growth
    description: Calculates period-over-period growth for a specified ward, category, and growth type, outputting results with formulas.
    input: Ward name, category name, growth type (e.g., MoM), and dataset.
    output: A structured table containing period, actual_spend, growth, formula, and notes.
    error_handling: Refuses calculation and raises errors if parameters are invalid or if aggregation is attempted.

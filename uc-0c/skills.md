# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the required columns, and reports any null actual_spend values before returning the rows.
    input: A path to the ward budget CSV file.
    output: A list of row dictionaries from the dataset.
    error_handling: If required columns are missing, stop and report the issue rather than proceeding.

  - name: compute_growth
    description: Computes growth for one ward and one category using the requested growth type and returns a per-period table.
    input: A list of dataset rows, a ward, a category, and a growth type.
    output: A list of rows containing period, actual spend, growth percentage, formula, and status.
    error_handling: If a null actual spend is encountered, mark the row as FLAGGED_NULL and do not compute a growth value.

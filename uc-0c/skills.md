# skills.md

skills:
  - name: load_dataset
    description: Load the budget CSV, validate its columns, and report missing values before returning the data.
    input: A CSV file path.
    output: A list of row dictionaries with validation notes for missing values.
    error_handling: If required columns are missing or the file cannot be read, raise an explicit error.

  - name: compute_growth
    description: Compute per-period growth for a specified ward and category using the requested growth type.
    input: A dataset, a ward, a category, and a growth type.
    output: A list of rows containing period, ward, category, actual spend, growth percentage, status, formula, and notes.
    error_handling: If the row has missing actual spend, mark it as flagged rather than computing it.

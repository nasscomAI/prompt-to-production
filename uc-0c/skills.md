skills:
  - name: load_dataset
    description: Reads the budget CSV, validates that all required columns are present, and reports the null count and reasons from the notes column before returning the data.
    input: file_path (string) - Path to the ward_budget.csv file.
    output: dataset (DataFrame) - A validated pandas DataFrame with null rows identified and logged.
    error_handling: Raise an instance of FileNotFoundError if the file is missing; refuse if columns 'ward', 'category', 'actual_spend' are absent.

  - name: compute_growth
    description: Calculates per-ward and per-category growth (e.g., MoM) for the dataset, returning a table that includes the mathematical formula for each calculation.
    input: ward (string), category (string), growth_type (string), dataset (DataFrame)
    output: growth_table (CSV format) - Per-period table showing actual spend, growth percentage, and formula; excludes null rows from computation.
    error_handling: Refuse and ask if growth_type is not provided; flag null rows as 'NULL - [reason]' in the output and do not compute values for them.

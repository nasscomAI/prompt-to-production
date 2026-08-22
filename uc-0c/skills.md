skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, validates its columns, and reports any null values found.
    input: Filepath of the CSV dataset (str).
    output: A list of dicts representing the rows.
    error_handling: Raise FileNotFoundError if the path is invalid, or ValueError if columns are missing.

  - name: compute_growth
    description: Filters data for a single ward/category and computes growth metrics with formula traceability.
    input: Dataset rows (list), ward (str), category (str), growth_type (str).
    output: A list of dicts with calculated growth, formulas, and notes.
    error_handling: Refuse and raise ValueError if aggregation is attempted or growth_type is missing.

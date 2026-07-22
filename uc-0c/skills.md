skills:
  - name: load_dataset
    description: Reads the CSV budget file, checks for required columns, counts and reports any null values in actual_spend, and returns the raw rows.
    input: File path to the input CSV file.
    output: List of dictionaries representing rows of the dataset.
    error_handling: Raises FileNotFoundError if file is missing, and ValueError if columns are missing.

  - name: compute_growth
    description: Takes ward, category, and growth type, validates inputs, filters rows, calculates MoM growth per period, formats formulas, flags nulls, and returns tabular results.
    input: Dictionary with keys 'rows', 'ward', 'category', 'growth_type'.
    output: List of dictionaries with calculated growth, formulas, and flags/notes.
    error_handling: Refuses and raises ValueError if inputs are invalid or incomplete.

# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports the null count and identifies which rows are null before returning.
    input: File path to the budget .csv data file.
    output: A validated list of dictionaries representing the dataset mapped row by row.
    error_handling: Return an error if essential columns are missing or if file cannot be read.

  - name: compute_growth
    description: Computes per-period growth for a specific ward and category using a defined growth type, showing the formula.
    input: Validated dataset, target ward, target category, and a specific growth_type.
    output: A per-period table detailing period, actual spend, computed growth, formula used, and flags/notes for nulls.
    error_handling: Refuse and return an error if growth_type is omitted, or if asked to aggregate across unknown or "all" wards/categories.

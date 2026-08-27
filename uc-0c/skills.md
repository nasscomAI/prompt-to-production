skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports the null count and specific null rows before returning the data.
    input: Path to the dataset CSV file (string).
    output: A validated dataset object along with a summary of null rows.
    error_handling: Refuses to load if required columns are missing and flags all null rows before proceeding.

  - name: compute_growth
    description: Computes growth per period for a specific ward and category, returning a table with formulas shown.
    input: Ward (string), category (string), growth_type (string, e.g., 'MoM'), and the loaded dataset.
    output: A per-period table (CSV/structured data) showing computed growth and the formula used for each row.
    error_handling: Refuses and asks if growth_type is not specified, refuses to compute across all wards/categories, and flags/skips computation for null rows reporting the reason.

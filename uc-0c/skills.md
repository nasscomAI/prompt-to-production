# skills.md — UC-0C Budget Growth

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the required columns, and reports any null values before returning the rows.
    input: Path to the CSV file.
    output: A list of dictionaries containing the CSV rows.
    error_handling: If required columns are missing or the file cannot be read, raise a clear error.

  - name: compute_growth
    description: Computes month-over-month growth for one ward/category pair, preserves null-row flags, and returns a row-level table with formulas.
    input: The loaded dataset plus a ward, category, and growth type.
    output: A list of dictionaries with period, actual_spend, growth_pct, formula, status, and notes.
    error_handling: If aggregation across wards/categories is requested, refuse rather than guessing.

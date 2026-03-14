# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count, and identifies which rows have nulls before returning the data.
    input: File path to the dataset CSV (string).
    output: A list of dictionaries containing the parsed rows, plus a printed validation report of null values.
    error_handling: Halts and raises an error if the input format is severely corrupt or essential columns are missing.

  - name: compute_growth
    description: Takes specific ward, category, and growth_type context, returning a per-period table with explicit formulas and results shown.
    input: Validated dataset (list of dicts), target ward (string), target category (string), and growth_type (string).
    output: A newly structured list of dictionaries ready for CSV export, explicitly containing a 'formula' column and flagged nulls.
    error_handling: Refuses to compute if attempting to aggregate across multiple wards/categories, and errors out definitively if growth_type is blank.

# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, validates columns, and identifies null values.
    input: File path (string) to `ward_budget.csv`.
    output: Dataset object/DataFrame and a report of null counts and specific rows with missing `actual_spend`.
    error_handling: Raise an error if the file is missing, columns are invalid, or if the data structure is unexpected.

  - name: compute_growth
    description: Calculates growth (MoM) for a specific ward and category, returning a per-period table with formulas.
    input: Ward name (string), Category (string), and growth_type (string).
    output: A table showing period, actual spend, growth percentage, and the formula used for each row.
    error_handling: Refuse to compute if growth_type is missing or if input parameters are ambiguous. Flag null rows instead of computing growth for them.

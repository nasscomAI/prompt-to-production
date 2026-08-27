# skills.md

skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate required columns, and identify null rows.
    input: A file path to `data/budget/ward_budget.csv`.
    output: A list of row dictionaries with validated budget data.
    error_handling: If required columns are missing, raise an error. If rows have null `actual_spend`, include them with null flags and retain the `notes` reason.

  - name: compute_growth
    description: Filter by ward and category, compute the requested growth type, and annotate each row with formula and growth values.
    input: Filtered data rows, ward string, category string, and growth_type string.
    output: A per-period table with `formula`, `growth`, and `null_flag` fields.
    error_handling: If the ward/category filter returns no rows, raise an error. If growth_type is missing or unsupported, refuse instead of guessing.

skills:
  - name: load_dataset
    description: Reads the CSV data, validates columns, and explicitly reports the count and exact rows of null values before returning the dataset.
    input: String path to the target CSV dataset (e.g., "../data/budget/ward_budget.csv").
    output: Validated dataset structure paired with a report of null `actual_spend` rows and their `notes`.
    error_handling: If the file is missing or format is malformed, raise an initialization error. Do not silently skip rows.

  - name: compute_growth
    description: Computes requested growth metric for a specific ward and category, returning a per-period table with explicit formula tracking.
    input: Target `ward` string, `category` string, and a valid `growth_type` identifier (e.g., "MoM").
    output: A per-period table (CSV structure) detailing period, actual spend, computed growth, and the literal formula applied.
    error_handling: If `--growth-type` is omitted or invalid, refuse and ask. If it hits a null `actual_spend` record, flag it and insert a specific null indicator rather than computing.

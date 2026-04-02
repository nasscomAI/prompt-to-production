skills:
  - name: load_dataset
    description: Loads the ward budget CSV, validates required columns, and reports null rows before returning the dataset.
    input: A CSV file path containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: A validated dataset and a report of rows where actual_spend is null.
    error_handling: If the file cannot be read, required columns are missing, or the dataset is malformed, return a clear error and do not continue with computation.

  - name: compute_growth
    description: Computes growth for a specific ward, category, and growth type and returns a per-period table with formulas shown.
    input: Validated dataset, ward name, category name, and growth_type.
    output: A per-period growth table with null rows flagged instead of computed.
    error_handling: If ward, category, or growth_type is invalid, or if the request implies all-ward aggregation, refuse rather than guessing or aggregating silently.

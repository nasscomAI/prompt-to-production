# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null actual_spend rows before returning the data.
    input: Path to a CSV file (e.g. ../data/budget/ward_budget.csv) with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: A DataFrame with validated rows, the count of null actual_spend rows, and a list of the null rows (period, ward, category, null reason from notes).
    error_handling: Raises a clear error if the file is missing or a required column is absent; returns null-row details rather than silently dropping or imputing.

  - name: compute_growth
    description: Computes the requested growth metric (e.g. MoM) for a single ward and category and returns a per-period table with the formula shown in every row.
    input: ward (string), category (string), growth_type (e.g. MoM), and the validated dataset from load_dataset.
    output: A per-period table with columns for period, actual_spend, growth value, null-flag status, null reason (if any), and the exact formula used (e.g. MoM = (current − previous) / previous × 100).
    error_handling: Refuses if growth_type is not specified; refuses cross-ward or cross-category aggregation; flags null actual_spend rows instead of computing or imputing.

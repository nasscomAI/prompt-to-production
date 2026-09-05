# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports the null count and which rows are null before returning.
    input: Path to the ward_budget.csv file.
    output: A validated dataset (rows) plus a report of how many actual_spend values are null and which rows (period, ward, category) they are.
    error_handling: Raises an error if the file is missing, columns are invalid, or the dataset cannot be parsed.

  - name: compute_growth
    description: Takes a ward, category, and growth type, and returns a per-period table with the formula shown on every row.
    input: Loaded dataset plus ward, category, and growth-type (MoM or YoY).
    output: A per-period table scoped to the requested ward and category, formula shown per row, null rows flagged with their reason.
    error_handling: Refuses (rather than guessing) if growth type is missing or if cross-ward/cross-category aggregation is requested.
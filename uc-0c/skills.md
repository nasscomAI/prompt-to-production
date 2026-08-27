skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates the schema, and returns the raw rows for processing.
    input: A CSV file path.
    output: A list of dataset rows with the required columns preserved.
    error_handling: Raise a clear error if the file is missing required columns or has no header row.

  - name: compute_growth
    description: Computes month-over-month growth without aggregating across ward or category boundaries.
    input: Dataset rows plus a growth type and optional ward/category filters.
    output: Output rows with actual spend, previous spend, growth result, formula, status, and null reason.
    error_handling: Refuse missing or unsupported growth types and reject all-ward/all-category aggregation requests.

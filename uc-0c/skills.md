skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, reports null count and identifies which rows.
    input: Dataset file path (string).
    output: Validated dataset structure, null count, and list of rows with null values.
    error_handling: Halts and alerts if required columns are missing or if file format is incorrect.

  - name: compute_growth
    description: Computes growth metrics for a given ward and category over time.
    input: ward (string), category (string), and growth_type (string, e.g., MoM).
    output: A per-period table showing period, actual spend, computed growth, and the formula used.
    error_handling: Returns an error if growth_type is not specified, and skips computation for null rows while reporting the null reason.

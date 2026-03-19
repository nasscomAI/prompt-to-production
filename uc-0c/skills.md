skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates its columns, and identifies data quality issues before processing.
    input: File path to the budget CSV document (String).
    output: A parsed dataset along with a report detailing the null count and the specific rows containing nulls (JSON/Dictionary).
    error_handling: Raises an error if the file is missing, cannot be read, or lacks the required columns.

  - name: compute_growth
    description: Calculates the specified growth metric for a specific ward and category over time.
    input: Validated dataset rows, target ward (String), target category (String), and growth_type (String).
    output: A per-period table of results including the calculated growth and the exact formula shown inline (JSON/Dictionary or String).
    error_handling: Refuses to compute and returns an alert if growth_type is missing/unrecognized or if an invalid aggregation across wards/categories is requested.

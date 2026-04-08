skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, reports null count and which rows have nulls before returning.
    input: CSV file path (string).
    output: Validated dataset table, null count, and list of specific rows with nulls.
    error_handling: If file is missing or schema is invalid, halt and report error.

  - name: compute_growth
    description: Computes period-over-period growth for a specific ward and category.
    input: ward (string), category (string), and growth_type (string, e.g., 'MoM' or 'YoY').
    output: A per-period table including results and the formula used alongside the result.
    error_handling: If growth_type is missing, refuse to compute and prompt the user. DO NOT guess this parameter.

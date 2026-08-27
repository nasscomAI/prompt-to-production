skills:
  - name: load_dataset
    description: Reads CSV, validates columns, and explicitly reports the null count and which rows are null before returning.
    input: CSV file path (string).
    output: Validated dataset along with a summary of null rows (count and explicit row details).
    error_handling: Fail and alert if required columns are missing.

  - name: compute_growth
    description: Computes growth per period for a given ward and category based on specified growth type.
    input: ward (string), category (string), and growth_type (string).
    output: Per-period table containing period, growth result, and the explicit formula used shown in every row.
    error_handling: Refuse and ask if growth_type is not provided. Flag uncomputable rows where actual_spend is null.

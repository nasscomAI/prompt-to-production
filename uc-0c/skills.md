# skills.md

skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning.
    input: CSV file path (string).
    output: Validated dataset and a summary of null rows containing their reasons.
    error_handling: If file is not found or columns are invalid, raise an error. If nulls exist, report them before proceeding.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown.
    input: ward (string), category (string), and growth_type (string, e.g., 'MoM').
    output: A per-period table showing the calculated growth and the explicit formula used.
    error_handling: If `--growth-type` is missing, refuse and ask. If `actual_spend` is null, flag it and skip computation for that row.

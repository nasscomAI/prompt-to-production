skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count
    input: file path
    output: parsed dataset
    error_handling: handle nulls
  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table
    input: parsed dataset
    output: output dataset
    error_handling: handle errors

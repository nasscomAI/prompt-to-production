skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: file_path (string)
    output: dataset array (list of objects) and specific null validation report showing null counts, affected rows, and notes
    error_handling: Fail immediately if input path is invalid or files are missing. Ensure no silent handling of null rows.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: ward (string), category (string), growth_type (string)
    output: per-period growth table mapping actual spend and percentage change, with formula column appended
    error_handling: Refuse to compute and throw an error if attempting to aggregate across multiple wards or categories. Refuse to compute and ask for input if growth_type is not explicitly provided.

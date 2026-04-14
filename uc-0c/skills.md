skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning
    input: CSV file path
    output: Validated dataset table, null count, and information on which rows are null
    error_handling: Fails and reports error if the file is missing or columns do not match the expected dataset structure

  - name: compute_growth
    description: Takes ward, category, and growth_type, returns per-period table with formula shown
    input: ward (string), category (string), growth_type (string)
    output: Per-period table displaying actual spend, computed growth, and the formula used
    error_handling: Refuses and asks if growth-type is not specified; flags null rows without computing

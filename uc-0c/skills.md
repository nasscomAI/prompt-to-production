skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: File path (string) to the budget CSV file
    output: Validated dataset (JSON/Dict) and a summary report of null rows and column structure
    error_handling: Return error message if file not found or if compulsory columns are missing

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: Filter parameters (ward, category, growth_type) and the loaded dataset
    output: Per-period growth table (string/CSV format) including the computation formula for each row
    error_handling: Refuse to compute and return error if growth_type is missing or if aggregation across wards/categories is attempted without explicit instruction

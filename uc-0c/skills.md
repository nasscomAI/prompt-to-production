skills:
  - name: load_dataset
    description: Reads CSV data and validates required columns and null rows.
    input: CSV file path
    output: Structured dataset with null row reporting
    error_handling: Refuses processing if required columns are missing

  - name: compute_growth
    description: Computes ward-level category growth calculations.
    input: ward, category, growth_type
    output: Per-period growth table with formulas shown
    error_handling: Refuses aggregation requests or missing growth type
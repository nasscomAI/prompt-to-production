skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null actual_spend rows with their reasons.
    input: CSV file path (expected ../data/budget/ward_budget.csv)
    output: DataFrame with all rows; null report printed to stdout before return.
    error_handling: If required columns missing, refuse and list missing columns.

  - name: compute_growth
    description: Computes per-period growth (MoM or YoY) for a single ward + category combination.
    input: DataFrame from load_dataset, ward string, category string, growth_type (MoM/YoY).
    output: Per-period table (CSV rows) with period, actual_spend, growth_pct, formula.
    error_handling: If growth_type not provided, refuse and ask. If ward/category not found, refuse and list available values.
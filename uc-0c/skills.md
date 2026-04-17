# skills.md

skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: path to ward_budget.csv
    output: structured dataset
    error_handling: Report null count and row details before proceeding

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: dataset, specific ward, category, and growth_type
    output: per-period table with formula
    error_handling: Refuse if aggregation across wards/categories is attempted or if growth_type is missing

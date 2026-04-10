skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and identifies all null actual_spend rows before computation.
    input:
      type: string
      format: File path to CSV (../data/budget/ward_budget.csv)
    output:
      type: object
      format: {
        "data": list of records,
        "null_rows": list of rows where actual_spend is null with period, ward, category, and notes
      }
    error_handling: >
      If file path is invalid → raise error and stop execution.
      If required columns are missing → raise validation error.
      If null values exist → do NOT remove them; return explicitly.

  - name: compute_growth
    description: Computes period-wise growth for a specific ward and category.
    input:
      type: object
      format: dataset + ward + category + growth_type
    output:
      type: list
      format: rows with period, actual_spend, growth, formula
    error_handling: >
      If ward/category not found → stop.
      If growth_type missing → refuse.
      If null → do NOT compute, return NULL.
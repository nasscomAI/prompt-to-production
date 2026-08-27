skills:
  - name: load_dataset
    description: Loads ward budget CSV data and validates required columns before analysis.
    input: File path to ward_budget.csv dataset.
    output: Structured dataset (list/dictionary) and report of null actual_spend rows.
    error_handling: If file missing or columns invalid, return error message and stop computation.

  - name: compute_growth
    description: Calculates period-wise growth for a specific ward and category using selected growth type.
    input: Structured dataset, ward name, category name, growth_type (e.g., MoM).
    output: Table of period, actual spend, growth percentage and formula used.
    error_handling: If actual_spend is null or previous value missing, flag row and skip growth calculation.
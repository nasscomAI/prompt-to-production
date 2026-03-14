# skills.md — UC-0C Budget Growth Skills

skills:
  - name: load_dataset
    description: Read the budget CSV, validate required schema, and report all null actual_spend rows before any analysis.
    input: "CSV path such as ../data/budget/ward_budget.csv."
    output: "Validated dataset plus metadata: column validation status, total row count, null actual_spend count, and detailed null rows (period, ward, category, notes)."
    error_handling: "If file missing/unreadable or required columns absent, return a hard validation error and stop. If period format is invalid, return parsing error with offending rows and do not compute growth."

  - name: compute_growth
    description: Compute period growth for a specific ward and category using an explicit growth_type and emit row-wise formulas.
    input: "Validated dataset + ward + category + growth_type (MoM or YoY)."
    output: "Per-period table for the selected ward/category with fields including period, actual_spend, comparison_period, comparison_value, formula, growth_percent, and status/flag."
    error_handling: "If growth_type missing/invalid, refuse and request a valid value. If ward/category not found, return scoped lookup error. If any required value is null or denominator is zero, mark row NOT_COMPUTED with reason; do not silently impute or skip."

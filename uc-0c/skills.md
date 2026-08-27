# skills.md — UC-0C Growth Calculation Skills

skills:
  - name: load_dataset
    description: Load CSV, validate schema, identify and report all null actual_spend rows before processing.
    input: File path to ward_budget.csv with columns {period, ward, category, budgeted_amount, actual_spend, notes}.
    output: Tuple of (dataframe, null_rows_list). null_rows_list contains {period, ward, category, reason} for each null. Raises error if schema invalid.
    error_handling: If file missing or columns invalid, raise error with details. If no nulls, return empty list. Continue even if nulls present.

  - name: compute_growth
    description: Compute MoM or YoY growth for specified ward + category combination, returning per-period table with formulas.
    input: Dataframe, ward name, category name, growth_type (MoM or YoY). All required.
    output: CSV-formatted string with columns {period, actual_spend, previous_spend, growth_rate, formula}. Each row includes calculation formula. Null periods shown with [NULL] marker.
    error_handling: If ward/category not in data, raise error. If growth_type not specified, raise error asking for MoM or YoY. If YoY requested with single-year data, refuse and explain.

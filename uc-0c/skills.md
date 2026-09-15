skills:
  - name: load_dataset
    description: Read the budget CSV, validate required columns, and report null actual_spend rows.
    input: Path to the ward budget CSV file.
    output: Parsed rows plus a list of rows where actual_spend is null.
    error_handling: If a required column is missing, stop and report the missing column name before any computation.

  - name: compute_growth
    description: Compute growth for one ward, one category, and one explicit growth type.
    input: Parsed dataset rows, a ward, a category, and a growth type.
    output: A per-period table including actual spend, growth result, and formula.
    error_handling: Refuse if ward or category scope is broad, if growth type is missing, or if a row has null actual_spend needed for the calculation.

skills:
  - name: load_dataset
    description: Read the budget CSV, validate schema, and report null actual_spend rows before analysis.
    input: "CSV file path for ward_budget data."
    output: "Validated dataset plus null report: {period, ward, category, notes} for each null actual_spend row."
    error_handling: "If required columns are missing or file cannot be parsed, stop with a schema/parsing error."

  - name: compute_growth
    description: Compute MoM or YoY growth for a specific ward and category and return period-level results with formulas.
    input: "Parameters: {ward, category, growth_type: MoM|YoY}."
    output: "Per-period rows: {period, actual_spend, formula, growth_pct, flag}."
    error_handling: "If growth_type is missing, refuse and ask; if a row has null actual_spend, set formula to NULL, growth_pct to NULL, and flag as SKIP."

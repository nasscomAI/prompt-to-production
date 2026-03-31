skills:
  - name: load_dataset
    description: "Reads the CSV budget file, validates the columns, and reports the null count with specific reasons before returning data."
    input: "String - Path to the budget CSV file."
    output: "A cleaned data structure containing the validated rows and a separate report of null rows."
    error_handling: "If required columns (period, ward, category, budgeted_amount, actual_spend) are missing, stop processing. Log each of the 5 deliberate null rows as a warning with the reason from the 'notes' column."

  - name: compute_growth
    description: "Takes the ward, category, and growth_type (MoM) and returns a per-period table with results and formulas shown."
    input: "Cleaned dataset, Ward name, Category name, Growth type (String)."
    output: "CSV/Table structure with columns: period, actual_spend, growth_result, formula_used, notes."
    error_handling: "If growth_type is missing or invalid, refuse to compute. If a computation period involves a null actual_spend, flag the row as 'NOT_COMPUTABLE' and state the reason."

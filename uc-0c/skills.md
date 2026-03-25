# skills.md — UC-0C Financial Budget Analysis Skills

skills:
  - name: load_dataset
    description: >
      Reads a CSV budget file, validates columns, and reports null count and reasons.
    input: File path (string) to the ward_budget.csv.
    output: A list of dictionaries (rows) and a summary report of null rows.
    error_handling: >
      If the file is missing, raises FileNotFoundError. If mandatory columns (period, ward, category)
      are missing, returns a validation error.

  - name: compute_growth
    description: >
      Calculates MoM or YoY growth for a specific ward and category, flagging nulls
      and showing the calculation formula.
    input: >
      Ward name (string), category name (string), and growth_type (MoM/YoY).
    output: >
      A formatted growth report (dataframe-like list) containing period, actual_spend, 
      growth_pct, formula, and notes.
    error_handling: >
      If growth_type is not provided, the skill refuses the operation. 
      If a row has null actual_spend, growth_pct is set to NULL and the reason is cited.

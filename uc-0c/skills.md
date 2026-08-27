skills:
  - name: load_dataset
    description: Reads the budget CSV file, ensures all required columns are present, and flags all null actual_spend rows.
    input: CSV file path (string) from `../data/budget/ward_budget.csv`.
    output: Validated dataset containing period, ward, category, budgeted_amount, actual_spend, and notes.
    error_handling: Refuses to load if core columns are missing; logs counts and reasons for null rows before returning results.

  - name: compute_growth
    description: Calculates MoM/YoY growth for a single ward-category pair, including the formula and flagging null spending.
    input: Selected ward (string), category (string), growth_type (string: MoM/YoY), and the validated dataset.
    output: Growth report (csv format) with growth percentages, the formula used, and notes for null-spend rows.
    error_handling: Refuses to run if growth_type is missing; refuses aggregation across multiple wards or categories as per enforcement rules.

# skills.md — UC-0C Budget Analyst Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates that all required columns exist, and identifies the 5 deliberate null rows.
    input: Path to 'ward_budget.csv' (String)
    output: A validated DataFrame and a summary report of rows where 'actual_spend' is NULL.
    error_handling: Raises a FileNotFoundError if the path is invalid and stops execution if columns are missing.

  - name: compute_growth
    description: Calculates the Month-over-Month (MoM) growth for a specific Ward/Category pair while showing the explicit formula used.
    input: Filtered Ward data (DataFrame), Growth Type (String: 'MoM')
    output: A table including 'growth_pct', 'formula', and a 'status' column for null reporting.
    error_handling: Refuses calculation and returns an error message if the previous month's data is missing or NULL.
# skills.md — UC-0C Budget Analyst

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates structure, and reports on data gaps (nulls).
    input: Path to a budget CSV file.
    output: A dataframe or list of dictionaries, plus a summary report of null count and their reasons.
    error_handling: Errors if required columns (period, ward, category, actual_spend) are missing.

  - name: compute_growth
    description: Calculates MoM or YoY growth for a specific ward and category, including the formula used.
    input: Dataset, ward name, category name, and growth_type (MoM/YoY).
    output: A table of results including period, spend, growth percentage, and formula.
    error_handling: Refuses to calculate if growth_type is missing or if the request implies aggregation across multiple wards/categories.

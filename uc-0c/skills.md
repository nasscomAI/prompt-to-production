# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates structure, and reports the count and location of null values before any processing.
    input: Path to the `ward_budget.csv` file.
    output: List of dictionaries (rows) and a summary log of detected nulls.
    error_handling: Refuses to return data if critical columns (period, ward, category, actual_spend) are missing.

  - name: compute_growth
    description: Filters data for a specific ward and category, then calculates MoM or YoY growth while documenting the formula.
    input: Dataset, ward name, category name, and growth type (MoM/YoY).
    output: A list of objects containing period, actual_spend, growth_value, formula, and null_flag status.
    error_handling: If a requested ward or category does not exist, it raises a validation error instead of returning empty results.

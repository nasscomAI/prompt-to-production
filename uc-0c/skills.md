# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports null counts and locations.
    input: Path to the ward_budget.csv file.
    output: A list of dictionaries representing the dataset and a summary of null rows.
    error_handling: If required columns (ward, category, actual_spend) are missing, raise a validation error.

  - name: compute_growth
    description: Calculates growth (MoM/YoY) for a specific ward and category.
    input: Ward name, category name, growth type, and the dataset.
    output: A list of results including period, actual spend, growth value, and the formula used.
    error_handling: If a null row is encountered in either the current or previous period, flag it and do not compute the growth for that period.

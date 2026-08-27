# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the columns, and checks for null values in 'actual_spend'.
    input: CSV file path (e.g., 'ward_budget.csv').
    output: A data structure with null counts and a map of which rows are null before any calculations start.
    error_handling: Logs an error and stops if critical columns are missing from the input file.

  - name: compute_growth
    description: Takes specified ward, category, and growth-type to compute a per-period budget growth table including formulas.
    input: The parameters 'ward', 'category', 'growth-type' (MoM/YoY), and the loaded budget dataset.
    output: A tabular representation with growth percentages and calculations shown.
    error_handling: Refuses to calculate if a required parameter is missing or if the current/previous period's data is null.

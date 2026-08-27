# skills.md — UC-0C Budget Analyst

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates schema integrity, and preemptively identifies all null actual_spend values.
    input: File path to ward_budget.csv.
    output: Validated dataset rows and a pre-computation report of all rows containing null actual_spend values with their reasons.
    error_handling: Raises a schema validation error if required columns are missing; logs an error if the file is unreachable.

  - name: compute_growth
    description: Calculates granular growth metrics (MoM/YoY) for a single ward-category pair, ensuring formula transparency.
    input: Specific Ward name, Category name, and Growth Type (MoM or YoY).
    output: A time-series table including period, spend, growth percentage, and the literal formula string used for the calculation.
    error_handling: Refuses to compute if inputs imply aggregation across wards/categories; flags null rows as 'Not Computed' and cites the reason from the dataset.

# skills.md — UC-0C Budget Analyst

skills:
  - name: load_dataset
    description: Ingests the budget CSV, verifies all columns (ward, category, actual_spend), and explicitly flags the 5 pre-identified null rows before returning the data.
    input: Absolute path to the ward_budget.csv file.
    output: A collection of records for a specific ward/category, indexed by period.
    error_handling: Identifying and reporting any row with an empty actual_spend field, citing the notes column for the reason.

  - name: compute_growth
    description: Calculates MoM or YoY growth based on specific ward and category parameters, ensuring that no aggregation across ward boundaries is performed.
    input: Parameters for current ward, current category, and the growth_type (MoM/YoY) to be used.
    output: A table including actual_spend, growth_percent, and the specific formula used for each period calculation.
    error_handling: Strictly refusing to proceed if growth_type is missing or if the request involves aggregating across multiple wards/categories.

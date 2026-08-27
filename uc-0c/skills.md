# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates mandatory columns, and reports the count and location of null actual_spend rows.
    input: File path to ward_budget.csv.
    output: Cleaned dataframe or structured data, along with a summary of detected nulls and their notes.
    error_handling: Fail if mandatory columns (period, ward, category, budgeted_amount) are missing; log a warning for every null actual_spend found.

  - name: compute_growth
    description: Calculates growth metrics for a specific ward and category based on the requested growth type, ensuring formulas are visible.
    input: Ward name, Category name, and growth_type (e.g., MoM).
    output: A per-period table containing period, actual_spend, growth result, and the formula used (e.g., "(Current - Previous) / Previous").
    error_handling: Refuse and ask for growth_type if missing; refuse global aggregation requests; flag and skip calculations for periods where actual_spend is NULL.


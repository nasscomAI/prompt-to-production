# skills.md — UC-0C Data Analysis Skills

skills:
  - name: load_dataset
    description: Parses the ward_budget.csv, validates required columns, and generates a pre-calculation report on all null rows and their reasons.
    input: CSV file path (ward_budget.csv).
    output: A structured object containing the budget data and an inventory of null entries with their notes.
    error_handling: Stop processing if critical columns (period, ward, category) are missing or if the file cannot be accessed.

  - name: compute_growth
    description: Calculates period-over-period growth for a specific ward and category, providing a transparent formula for each step.
    input: Dataset filtered by one ward and one category, and the specified growth type (MoM or YoY).
    output: A per-period table including actual spend, calculated growth (%), and the formula used.
    error_handling: Do not calculate growth for periods involving null values; instead, flag the row as 'Flagged (NULL)' and include the reason.

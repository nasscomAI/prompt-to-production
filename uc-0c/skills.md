# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and identifies rows with null 'actual_spend' values for transparent reporting.
    input: Path to the ward_budget.csv file.
    output: A cleaned list of row dictionaries and a separate report of null rows found.
    error_handling: Reports the exact count and periods of null values found before processing.

  - name: compute_growth
    description: Calculates the growth (MoM) between periods for a specific ward and category, strictly showing the mathematical formula for each step.
    input: Filtered data for a specific ward/category and the growth_type (e.g., MoM).
    output: A list of results including the period, actual spend, growth percentage, and the formula used.
    error_handling: Refuses to compute if the previous period is missing or if the current period has a NULL value.

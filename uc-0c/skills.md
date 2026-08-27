# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the expected columns, and performs a pre-computation scan to identify any null values and their reasons.
    input: CSV file path.
    output: Data structure containing clean rows and a separate report of null/missing rows.
    error_handling: Refuses to proceed if required columns like 'actual_spend' or 'budgeted_amount' are missing.

  - name: compute_growth
    description: Calculates Month-over-Month (MoM) or Year-over-Year (YoY) growth for a specific ward and category, generating a table that includes the growth percentage and the formula used.
    input: Ward name, Category, Growth Type (MoM/YoY), and the loaded dataset.
    output: A table of results including Period, Actual Spend, Growth %, and Formula.
    error_handling: Returns a 'NULL' flag with the reason for periods where data is missing; refuses to calculate if growth-type is missing.

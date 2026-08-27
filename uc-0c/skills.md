skills:
  - name: load_dataset
    description: Loads the ward budget dataset and validates its structure before analysis.
    input: Path to ward_budget.csv file.
    output: Structured dataset containing rows grouped by ward, category, and period.
    error_handling: If required columns are missing or the file cannot be read, return an error and stop execution.

  - name: compute_growth
    description: Computes growth metrics for a specific ward and category based on the chosen growth type.
    input: Dataset rows filtered by ward and category, and the growth type (MoM or YoY).
    output: Table containing period, actual_spend, growth value, and formula used.
    error_handling: If actual_spend is null for a period, flag the row and report the reason from the notes column instead of computing growth.

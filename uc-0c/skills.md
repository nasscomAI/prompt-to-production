# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the budget CSV and performs initial validation for null values.
    input: Path to CSV file.
    output: List of row dictionaries.
    error_handling: Fail if critical columns (actual_spend, budgeted_amount) are missing.

  - name: compute_growth
    description: Calculates month-over-month (MoM) growth for a filtered subset of data.
    input: Filtered list of rows, growth type (MoM).
    output: List of results with growth percentage and formula.
    error_handling: Return "NULL" and the note if a required value is missing.

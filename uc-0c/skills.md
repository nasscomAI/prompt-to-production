# skills.md — UC-0C Financial Growth Analyst

skills:
  - name: load_dataset
    description: Reads the municipal budget CSV and performs initial data validation and null-value reporting.
    input: Path to the ward_budget.csv file.
    output: A cleaned DataFrame or list of records, and a summary of any identified null values and their corresponding notes.
    error_handling: If required columns (ward, category, period, actual_spend) are missing, stop execution and report the schema error.

  - name: compute_growth
    description: Calculates Month-over-Month (MoM) or Year-over-Year (YoY) growth for a specific ward and category.
    input: A dictionary containing ward (string), category (string), and growth_type (string: 'MoM' or 'YoY').
    output: A table or list of rows, each containing the period, actual spend, growth result, and the formula used.
    error_handling: If a null spend value is encountered, do not compute growth for that period; instead, mark the row with the reason from the notes.

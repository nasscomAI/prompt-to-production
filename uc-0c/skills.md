# skills.md — UC-0C Budget Growth Analyst

skills:
  - name: load_dataset
    description: Load the ward budget CSV, perform column validation, and proactively identify all null values in the actual_spend column.
    input: File path to the ward_budget.csv file.
    output: A list of dictionaries representing the validated dataset and a summary report of any identified null rows.
    error_handling: "Fail if mandatory columns (period, ward, category, budgeted_amount, actual_spend) are missing."

  - name: compute_growth
    description: Perform MoM or YoY growth calculations for a specific ward and category while enforcing formula transparency and null flagging.
    input: Dictionary containing ward, category, growth_type, and list of row data.
    output: A list of dictionaries with columns showing period, actual spend, growth percentage, and the calculation formula.
    error_handling: "Return 'NULL' with a reason if input data is missing for the period; refuse to calculate if growth_type is ambiguous."

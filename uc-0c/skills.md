skills:
  - name: "load_dataset"
    description: "Reads the budget CSV, validates the column structure, and identifies the 5 deliberate null actual_spend rows."
    input: "File path to ward_budget.csv."
    output: "A filtered dataset and a report of null rows found with their corresponding notes."
    error_handling: "If the input file is missing the 'actual_spend' or 'notes' columns, stop and report a schema error."

  - name: "compute_growth"
    description: "Calculates MoM growth for a specific ward and category, returning a table that includes the formula and flags for null periods."
    input: "Filtered data, ward name, category name, and growth_type (MoM)."
    output: "A CSV-formatted table (growth_output.csv) with columns for Period, Actual Spend, MoM Growth, and Formula."
    error_handling: "If a calculation involves a null 'actual_spend' row, mark the growth as 'NULL_FLAGGED' and include the reason from the notes."
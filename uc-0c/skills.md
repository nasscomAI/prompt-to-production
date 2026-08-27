# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the columns (period, ward, category, budgeted_amount, actual_spend, notes), and reports null counts and their reasons.
    input: File path (string) to the ward_budget.csv file.
    output: A validated dataset object or dataframe, with a summary of identified null rows and notes.
    error_handling: Refuses to process if required columns are missing, if the file is unreadable, or if it cannot access the 'actual_spend' or 'notes' columns.

  - name: compute_growth
    description: Calculates growth metrics (e.g., MoM) for a specific ward and category, returning a per-period table with growth percentages and the formulas used.
    input: Ward name (string), category name (string), and growth_type (string, e.g., 'MoM').
    output: A per-period table (CSV or structured object) containing period, actual spend, growth percentage, and the explicit formula.
    error_handling: Refuses calculation if growth_type is not specified, or if the ward/category combination is not found in the dataset. Flags null rows as 'not computed' with the reason from the dataset.

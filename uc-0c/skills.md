skills:
  - name: load_dataset
    description: Reads the ward_budget.csv, validates the 300 rows, and identifies the 5 deliberate null actual_spend rows.
    input: File path to the budget CSV (string).
    output: A structured dataset including the 'notes' column for all rows.
    error_handling: Reports a specific error if the CSV is missing columns or if fewer than 300 rows are found.

  - name: compute_growth
    description: Filters data by ward/category and calculates MoM growth while showing the formula used.
    input: Filtered dataset, ward name, category name, and growth_type.
    output: A table including period, actual_spend, growth_pct, and the specific formula used.
    error_handling: Refuses to calculate for rows where actual_spend is NULL; instead, returns 'NOT_COMPUTED' and citations from the notes.

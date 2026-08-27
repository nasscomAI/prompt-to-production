# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the columns, and identifies all rows with null 'actual_spend' values.
    input: Path to the budget CSV file.
    output: A list of row dictionaries and a summary of identified null rows.
    error_handling: Reports specific rows that are missing critical columns like 'period' or 'ward'.

  - name: compute_growth
    description: Calculates growth (MoM or YoY) for a specific ward and category, including the formula in the output.
    input: Ward name, Category name, growth type (MoM/YoY), and the dataset.
    output: A list of dictionaries containing period, actual_spend, growth_value, formula, and flags/notes.
    error_handling: Refuses to calculate growth for periods where the previous or current 'actual_spend' is null, reporting the note instead.


skills:
  - name: load_dataset
    description: Reads the CSV budget data, validates the presence of all 6 mandatory columns, and identifies all rows where actual_spend is null.
    input: File path to ward_budget.csv (string).
    output: A validated dataset and a summary report of null rows found (including the count and specific notes for each null).
    error_handling: Refuse to process if mandatory columns are missing; stop and report if file is not found or is not a valid CSV.

  - name: compute_growth
    description: Calculates MoM or YoY growth for a specific ward and category, strictly adhering to null-handling and formula-transparency rules.
    input: Ward name (string), Category name (string), and Growth Type (string: MoM or YoY).
    output: A structured table containing Ward, Category, Period, Growth Value, and the exact Formula used for the calculation.
    error_handling: If growth type is not provided, refuse and ask; if a null actual_spend row is encountered, skip the calculation and output the flag/reason from notes instead of a result.

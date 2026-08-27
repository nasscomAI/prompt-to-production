skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and identifies all rows with null actual_spend values.
    input: Path to the ward_budget.csv file (string).
    output: List of validated records including null row metadata.
    error_handling: Report the specific notes for any null row and fail if key columns like 'ward' or 'category' are missing.

  - name: compute_growth
    description: Calculates MoM or YoY growth for a specific ward and category while preserving formula transparency.
    input: Ward name, Category, and Growth Type (MoM/YoY).
    output: Result table containing period, actual_spend, growth percentage, and the formula used.
    error_handling: If '--growth-type' is not provided, or if the specified ward/category combination is not found, return an error message instead of calculating.


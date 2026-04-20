# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the column structure, and pre-identifies all rows with null actual_spend values.
    input: Path to the budget CSV file.
    output: A validated dataset object and a mapping of rows with missing spend values.
    error_handling: Fail if mandatory columns (period, ward, category, budgeted_amount) are missing.

  - name: compute_growth
    description: Calculates MoM or YoY expenditure growth for a filtered ward and category, including mandatory formula disclosure.
    input: Ward string, Category string, Growth Type (MoM/YoY), and the validated dataset.
    output: A period-by-period table with Actual Spend, Growth Percentage, and the Formula string.
    error_handling: Explicitly refuse and ask for specification if growth_type is missing or if all-ward aggregation is requested.

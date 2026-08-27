skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and identifies all null 'actual_spend' rows before returning the data.
    input: Path to the `ward_budget.csv` file.
    output: A validated dataset object and a report of identified null rows with their reasons.
    error_handling: Refuses to proceed if the file is missing or required columns (period, ward, category) are absent.

  - name: compute_growth
    description: Calculates growth for a specific ward and category based on the requested growth type, ensuring results are granular and formulas are shown.
    input: Ward name, Category name, Growth type (MoM/YoY), and validated dataset.
    output: A table of growth results per period with the formula displayed for each row.
    error_handling: Returns an explicit refusal if asked for a cross-ward or cross-category aggregation.

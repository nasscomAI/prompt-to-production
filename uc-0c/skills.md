skills:
  - name: load_dataset
    description: Loads the budget dataset and validates all required columns.
    input: CSV file path
    output: Validated dataset with null report
    error_handling: Stop if required columns are missing and report null rows.

  - name: compute_growth
    description: Calculates MoM or YoY growth for a selected ward and category.
    input: Dataset, ward, category, growth_type
    output: Per-period growth table with formulas
    error_handling: Refuse if ward/category is ambiguous or growth_type is missing.
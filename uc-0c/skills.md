# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates essential columns, and identifies all null rows with their associated notes.
    input: file_path (string)
    output: Validated dataset structure and a summary of null entries including their count and specific ward/category/period.
    error_handling: Stop and report if mandatory columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing or if the file format is invalid.

  - name: compute_growth
    description: Calculates growth (MoM/YoY) for a filtered subset (ward + category) and generates a detailed report with formulas.
    input: ward (string), category (string), growth_type (string)
    output: Table containing Period, Actual Spend, Growth Percentage, and the explicit Formula used for each calculation.
    error_handling: Refuse calculation if growth_type is unknown or missing; for null rows, skip calculation and output the reason from the 'notes' column.

# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports all null actual_spend values with their reasons.
    input: Path to the budget CSV file.
    output: A validated dataset (list of dicts) and a report of null rows.
    error_handling: If the file is missing or columns are incorrect, returns a critical error.

  - name: compute_growth
    description: Calculates growth metrics for a specific ward and category based on the growth type.
    input: Validated dataset, ward name, category name, and growth_type (MoM/YoY).
    output: A table containing period, actual spend, growth percentage, and the formula used.
    error_handling: If a value is null, the growth is marked as 'NULL' and the reason is cited; no calculation is performed for that period.

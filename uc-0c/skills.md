# skills.md


skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the required columns, and reports the count and details of null actual_spend rows.
    input: File path to the CSV dataset (string).
    output: A validated data structure and a summary of null rows.
    error_handling: Refuse if required columns (period, ward, category, budgeted_amount, actual_spend) are missing.

  - name: compute_growth
    description: Calculates growth metrics for a specific ward and category based on the requested growth type.
    input: Ward name (string), category name (string), and growth_type (string, e.g., MoM).
    output: A per-period table containing period, actual spend, growth value, and the formula used.
    error_handling: Refuse if growth_type is missing or if the ward/category combination does not exist.


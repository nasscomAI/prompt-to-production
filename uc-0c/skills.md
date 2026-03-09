skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and identifies all null actual_spend rows.
    input: CSV file path.
    output: A list of dicts representing the dataset, and a report of detected nulls.
    error_handling: Raise error if 'ward', 'category', 'actual_spend', or 'period' columns are missing.

  - name: compute_growth
    description: Calculates period-over-period growth for a specific ward and category.
    input: Dataset (list), ward (str), category (str), growth_type (str).
    output: A list of results including period, actual_spend, growth_value, and formula.
    error_handling: Refuse if ward or category are not found or not unique. Refuse if growth_type is invalid or missing. Flag NULL rows instead of computing growth when actual_spend is missing for current or previous period.

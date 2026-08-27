# skills.md — UC-0C Number That Looks Right

skills:
  - name: filter_by_ward_and_category
    description: Filter budget CSV rows to select only rows matching specified ward AND category.
    input: CSV data (list of dicts), ward name (string), category name (string).
    output: Filtered list of rows (list of dicts) with matching ward and category only.
    error_handling: If no rows match, return empty list. If ward or category not found, return empty list (do not create synthetic rows). Case-sensitive matching against column values.

  - name: calculate_totals
    description: Sum budgeted_amount and actual_spend for filtered rows, counting nulls separately.
    input: Filtered list of rows (list of dicts).
    output: Dictionary with total_budgeted, total_actual_spend, null_count, variance, months_with_data.
    error_handling: If actual_spend is null for a row, do not include in sum (note null). If all rows are null, output total_actual_spend as null and variance as 'Cannot calculate'. If input is empty, output all zeros and null_count=0.

  - name: calculate_growth
    description: Calculate month-over-month or year-over-year growth in actual_spend (if non-null).
    input: Filtered rows with period field (YYYY-MM), growth_type (MoM or YoY).
    output: Dictionary mapping period to growth_percentage, or 'N/A' if prior period is null or unavailable.
    error_handling: If current or prior period has null actual_spend, return 'N/A' for that growth. If first month in dataset, return 'N/A' for growth. Do not interpolate missing months.

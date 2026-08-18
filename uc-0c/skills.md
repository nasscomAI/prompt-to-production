skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports any null actual_spend rows.
    input: Path to the CSV file.
    output: Dataset records along with a summary of detected null values and reasons.
    error_handling: Raises an error if required columns (period, ward, category, budgeted_amount, actual_spend) are missing.

  - name: compute_growth
    description: Calculates growth (MoM/YoY) per period for a specific ward and category, returning a table with the formula.
    input: Dataset records, ward name, category name, and growth_type.
    output: Table containing period, actual spend, growth percentage, and formula used, or a flagged null message.
    error_handling: Refuses computation and returns a clean error if growth_type is missing or if requested to aggregate across wards/categories without explicit instruction.

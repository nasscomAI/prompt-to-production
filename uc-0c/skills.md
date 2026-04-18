# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads CSV file, validates columns, reports null count and which rows before returning the dataset, ensuring silent null handling is avoided.
    input: File path to CSV (string).
    output: Pandas DataFrame with validated data, plus a report of nulls (dict with count and list of null rows including notes).
    error_handling: If columns are missing or invalid, return error with details and do not proceed; always report nulls explicitly.

  - name: compute_growth
    description: Takes ward, category, and growth_type, computes per-period growth table with formulas shown, avoiding wrong aggregation level and formula assumption.
    input: DataFrame, ward (string), category (string), growth_type (string: 'MoM' or 'YoY').
    output: List of dicts (one per period) with period, actual_spend, growth_rate, formula, and null flags; no aggregation across wards/categories.
    error_handling: If ward/category not found or growth_type invalid, return error; flag nulls with reasons and refuse invalid growth_type.

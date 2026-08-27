skills:
  - name: load_dataset
    description: Reads the CSV from --input, validates the 5 expected columns, reports null count and which specific rows have null actual_spend before returning the DataFrame.
    input: CSV file path (string).
    output: Tuple of (DataFrame, list) — the validated dataset and a list of dicts describing each null row: {period, ward, category, null_reason}.
    error_handling: Raises FileNotFoundError if the CSV path does not exist; raises ValueError if any of the 5 required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing.

  - name: compute_growth
    description: Takes a filtered ward+category subset and a growth_type ("MoM" or "YoY"), returns a per-period table with growth_rate, null_flag, null_reason, and formula_used for each row.
    input: DataFrame (filtered to one ward and one category), growth_type (string, must be "MoM" or "YoY").
    output: DataFrame with columns — period, actual_spend, growth_rate (float or "NULL"), null_flag (True/False), null_reason (string or ""), formula_used (string showing the formula applied for that row).
    error_handling: Raises ValueError if growth_type is not "MoM" or "YoY"; raises ValueError if the input DataFrame spans multiple wards or categories; returns "NULL" for growth_rate and records the notes reason for any row where actual_spend is null.

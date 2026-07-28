# skills.md

skills:
  - name: load_dataset
    description: Reads a ward-budget CSV, validates required columns, and reports null counts and locations in actual_spend before returning.
    input: CSV file path (string)
    output: Pandas DataFrame with validated columns; also prints null row count and the (period, ward, category, notes) for each null.
    error_handling: If the file is missing or required columns are absent, raises a clear error and stops. If all data is valid, prints confirmation.

  - name: compute_growth
    description: Given a ward, category, and growth type, filters the loaded dataset and returns a per-period table with actual_spend, computed growth, a null flag/reason if applicable, and the formula string.
    input: DataFrame, ward (string), category (string), growth_type (string — "MoM" or "YoY")
    output: DataFrame with columns [period, actual_spend, growth, null_reason, formula]; printed row-by-row for auditability.
    error_handling: If growth_type is missing or not "MoM"/"YoY", refuses and asks. If no rows match the ward+category filter, reports zero matches. Null actual_spend rows show "NOT COMPUTED — <notes>" in growth and formula columns.

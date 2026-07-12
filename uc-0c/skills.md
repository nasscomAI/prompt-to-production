skills:
  - name: load_dataset
    description: Reads a CSV, validates required columns, reports null count and which rows contain null actual_spend before returning the DataFrame.
    input: Path to a CSV file with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: A pandas DataFrame with validated columns; also prints a report of null rows and their notes.
    error_handling: Raises FileNotFoundError if the CSV does not exist. Raises ValueError if required columns are missing or the file is empty.

  - name: compute_growth
    description: Computes per-period growth for a specific ward and category using the specified growth type, showing the formula alongside each result.
    input: DataFrame filtered to one ward and category, growth_type string (MoM or YoY), period column name.
    output: A DataFrame with columns period, actual_spend, growth_type, growth_value, formula (e.g. "((current - previous) / previous) * 100"), and a flag column noting any null rows that were skipped.
    error_handling: Refuses to compute if growth_type is not provided; refuses to aggregate across wards or categories; flags null actual_spend rows instead of computing; raises ValueError if fewer than 2 periods exist for growth calculation.

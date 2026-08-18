# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads a CSV file, validates required columns, and reports null count and specific null rows before returning the data.
    input: File path to a CSV file (string) with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: DataFrame or list of rows (structured data) with validation report including null details.
    error_handling: Raises an error if required columns are missing, file is unreadable, or null rows are not properly flagged.

  - name: compute_growth
    description: Takes a specific ward, category, and growth type, and returns a per-period table with actual spend, growth percentage, and formula.
    input: Ward name (string), category name (string), growth type (string: 'MoM' or 'YoY'), and dataset (structured data).
    output: Table (list of dictionaries) with period, actual_spend, growth, formula; nulls flagged with reasons.
    error_handling: Refuses if growth type is unspecified or invalid; flags nulls without computing; refuses aggregation across wards/categories.

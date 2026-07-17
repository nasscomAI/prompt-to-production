# skills.md — UC-0C Budget Growth

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning data.
    input: File path string to a CSV file.
    output: Dictionary with keys: rows (list of dicts), null_rows (list of dicts with notes), column_names (list of strings).
    error_handling: Returns empty rows list and logs error if file not found or columns invalid.

  - name: compute_growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown.
    input: ward (string), category (string), growth_type (MoM or YoY), rows (list of dicts from load_dataset).
    output: CSV with columns: period, actual_spend, growth_percentage, formula. Null rows flagged with reason.
    error_handling: If growth_type not specified, raises ValueError. If no data for ward/category, returns empty table.

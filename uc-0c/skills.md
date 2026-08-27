# skills.md

skills:
  - name: load_dataset
    description: Reads budget CSV, validates column structure, and reports null values with their reasons before returning clean data.
    input: File path (string) pointing to budget CSV file.
    output: Dict with keys={"data": cleaned_dataframe, "null_rows": list_of_null_info, "summary": {"total_rows": int, "null_count": int}}. null_rows contains {period, ward, category, reason}.
    error_handling: If columns missing, raise ValueError with list of missing columns. If no data rows found, raise ValueError. If null rows detected, include them in output but do NOT remove them from data.

  - name: compute_growth
    description: Calculates per-period growth metric (MoM or YoY) for a specified ward and category with formulas shown.
    input: Dict {"ward": string, "category": string, "growth_type": "MoM" or "YoY", "data": dataframe from load_dataset}.
    output: DataFrame with columns=[period, actual_spend, formula_used, growth_percent, null_flagged]. Each row shows the formula (e.g., "(19.7-14.8)/14.8").
    error_handling: If ward or category not found, raise ValueError. If growth_type not in ["MoM", "YoY"], raise ValueError. If null rows exist in result set, include them with null_flagged=True and growth_percent=None.

# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Read ward budget CSV, validate columns, report null count and which rows before returning structured data
    input: file_path (str — path to ward_budget.csv)
    output: dict with keys: rows (list of dicts), null_rows (list of dicts with period, ward, category, notes), wards (set), categories (set)
    error_handling: If file not found, raise FileNotFoundError. If required columns missing, raise ValueError. If no data rows, raise ValueError. Log warning for each null actual_spend found.

  - name: compute_growth
    description: Filter data by ward + category, compute MoM growth per period with formula shown, flag nulls
    input: rows (list of dicts), ward (str), category (str), growth_type (str — "MoM" or "YoY")
    output: list of dicts with keys: period, actual_spend, growth_pct, formula, null_flag, null_reason
    error_handling: If ward/category combination has no rows, raise ValueError. If growth_type not in ["MoM", "YoY"], raise ValueError. If insufficient data for growth computation, return available periods with N/A for first period.
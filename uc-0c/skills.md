skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null actual_spend rows before returning data.
    input: "file_path (str, path to ward_budget.csv)."
    output: "list of dicts (period, ward, category, budgeted_amount: float, actual_spend: float or None, notes: str). Also prints a null report to stdout: count of null rows and their period/ward/category/reason."
    error_handling: "Raises ValueError if required columns (period, ward, category, budgeted_amount, actual_spend) are missing from the header. A blank actual_spend is parsed as None, never as 0.0 or dropped from the returned rows."

  - name: compute_growth
    description: Computes per-period growth for one ward+category, showing the formula used, and refusing to guess on missing inputs or data.
    input: "rows (list from load_dataset), ward (str), category (str), growth_type (str, 'MoM' or 'YoY')."
    output: "list of dicts (period, actual_spend, growth_pct, formula, flag) for every period matching ward+category, in period order."
    error_handling: "If ward or category is missing/empty/'all', returns a refusal result instead of computing anything. If growth_type is missing or not one of MoM/YoY, returns a refusal result. If a period's actual_spend (or the prior period it depends on) is null, that row's growth_pct is left blank and flag explains why, instead of raising or silently defaulting."

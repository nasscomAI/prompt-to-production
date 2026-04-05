# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Load the budget CSV, validate columns, report null counts and locations, return full dataset ready for filtering.
    input: File path to ward_budget.csv with columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: DataFrame with all rows. For each null actual_spend: log (period, ward, category, notes reason). Return null_count and null_rows_list.
    error_handling: If file not found, raise FileNotFoundError. If columns missing, raise ValueError with missing column names. If CSV malformed, log parse errors and continue.

  - name: compute_growth
    description: Filter to exact ward + category, compute growth per period, return per-period table with formulas shown.
    input: DataFrame, ward (string exact match), category (string exact match), growth_type ("MoM" or "YoY").
    output: DataFrame with columns: period, actual_spend, formula_used, growth_pct. For nulls, set growth_pct to null and formula_used to "DATA_NULL — reason from notes". For first period, growth_pct is blank (no prior period). For valid periods, show MoM or YoY formula.
    error_handling: If ward or category not in dataset, raise ValueError with exact values that exist. If growth_type is neither MoM nor YoY, raise ValueError asking user to specify. Always flag nulls, never skip them.

# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates the expected columns are present, and reports the null actual_spend rows before returning any data.
    input: path (str) to ward_budget.csv.
    output: list of row dicts {period, ward, category, budgeted_amount (float), actual_spend (float or None), notes (str)}; also prints a report of total rows and each null row (period/ward/category/reason).
    error_handling: Raises ValueError listing any missing required columns; raises IOError if the file cannot be read; never coerces a blank actual_spend to 0 — it is kept as None.

  - name: compute_growth
    description: Computes a per-period growth table for one ward + one category + one growth type, showing the formula used for every row.
    input: rows (from load_dataset), ward (str), category (str), growth_type ("MoM" or "YoY").
    output: list of dicts {period, ward, category, budgeted_amount, actual_spend, formula, growth_pct, flag, note} — one row per period for that ward+category, sorted by period.
    error_handling: If ward+category matches zero rows, raises ValueError naming the ward/category so the caller knows the filter was wrong rather than getting a silent empty table; for any row where the current or required prior actual_spend is null/unavailable, growth_pct is left blank and flag/note explain why instead of computing a number.

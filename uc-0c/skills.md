# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, reports null actual_spend count and which rows with notes before returning structured data.
    input: input_path (str — path to CSV, expected ../data/budget/ward_budget.csv; must end with .csv and exist)
    output: dict with keys {rows: list[dict] (each dict has period, ward, category, budgeted_amount (float), actual_spend (float|None), notes (str)), columns: list[str], null_count: int, null_rows: list[dict] (each has period, ward, category, notes), total_rows: int}; example {"total_rows": 300, "null_count": 5, "null_rows": [{"period":"2024-03","ward":"Ward 2 – Shivajinagar","category":"Drainage & Flooding","notes":"Data not submitted by ward office"}]}
    error_handling: If file does not exist, does not end with .csv, is empty, or missing required columns [period, ward, category, budgeted_amount, actual_spend, notes], return {"error": "invalid input — <reason>"} and caller must refuse to compute; never coerce null to 0, never drop null rows silently, always report null count and list before returning.

  - name: compute_growth
    description: Takes ward + category + growth_type and structured dataset, returns a per-ward per-category per-period table with growth and formula shown for every row, flagging nulls.
    input: dataset (dict from load_dataset — rows/null_rows), ward (str — single ward name, required), category (str — single category name, required), growth_type (str — required, one of ["MoM","YoY"] case-insensitive)
    output: list[dict] — one dict per period sorted ascending (12 rows for 2024-01 to 2024-12) with keys {period (YYYY-MM), ward, category, budgeted_amount (float), actual_spend (float|None), growth_pct (float|None or "NULL"), formula (str), notes (str), flag (str)}; MoM growth_pct = (curr-prev)/prev*100 for valid consecutive months, YoY = (curr-same_month_prev_year)/same_month_prev_year*100; formula examples: "(19.7-14.8)/14.8" for 2024-07, "N/A (no prior period)" for 2024-01, "FLAGGED NULL — Data not submitted by ward office" for null rows, "N/A (prior period flagged NULL: <notes>)" when prev is null.
    error_handling: If ward or category is missing/empty/"all"/"any", return {"error": "[REFUSE] Aggregation across wards/categories not allowed — specify a single --ward and --category"}; if growth_type is missing/empty/not in [MoM,YoY], return {"error": "[REFUSE] --growth-type is required — specify MoM or YoY, will not assume formula"}; if ward/category not found, return {"error": "invalid input — ward/category not found: <value>"}; if dataset has error key, propagate error and do not compute; never guess formula, never silently aggregate, never compute over null as 0.

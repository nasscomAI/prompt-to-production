# skills.md

skills:
  - name: load_dataset
    description: Read ward_budget.csv, validate schema, and report null actual_spend rows before any computation.
    input: "input_path (string path to ward_budget.csv, UTF-8 with en-dash U+2013 in ward names; expected columns period,ward,category,budgeted_amount,actual_spend,notes). Example: '../data/budget/ward_budget.csv'."
    output: "Dict with rows (list of dicts in file order), columns (validated header list), null_count (int, expected 5), null_rows (list of {period, ward, category, notes} for every blank actual_spend). Example: {'null_count': 5, 'null_rows': [{'period': '2024-03', 'ward': 'Ward 2 – Shivajinagar', 'category': 'Drainage & Flooding', 'notes': 'Data not submitted by ward office'}, ...]}."
    error_handling: If file is missing/unreadable, raise FileNotFoundError with the path. If required columns are missing, raise ValueError naming the missing columns — never proceed with a partial schema. Never fill, drop, or interpolate null actual_spend rows; always report them with their verbatim notes reason.

  - name: compute_growth
    description: Compute per-period MoM growth for one ward + category slice per agents.md enforcement, with formula shown.
    input: "Dict from load_dataset plus ward (exact string, e.g. 'Ward 1 – Kasba'), category (exact string, e.g. 'Roads & Pothole Repair'), growth_type (must be 'MoM'). Only rows matching ward + category byte-identically are used, ordered by period 2024-01..2024-12."
    output: "List of 12 dicts with period,ward,category,actual_spend,growth_pct,formula,flag in period order. First period has blank growth_pct/formula with flag 'BASE — no prior period'. Null actual_spend rows (current or prior) have blank growth_pct/formula and flag 'NULL — <verbatim notes>'. Computed rows use growth_pct = (curr − prev) / prev × 100 rounded to 1 decimal with sign (e.g. '+33.1%', '−34.8%') and formula with substituted values (e.g. '(19.7 − 14.8) / 14.8 × 100 = +33.1%'). Example reference: Ward 1 – Kasba / Roads & Pothole Repair 2024-07 → +33.1%, 2024-10 → −34.8%."
    error_handling: If growth_type is missing/empty/unsupported, REFUSE with an error asking the caller to specify a supported value — never default silently. If ward/category does not byte-match dataset values, REFUSE listing valid values — never fuzzy-match. If asked to aggregate across wards/categories into one number, REFUSE with an aggregation-level error — always return the per-period slice table.

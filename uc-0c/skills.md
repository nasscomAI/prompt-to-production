# skills.md

skills:
  - name: load_dataset
    description: Load budget CSV, validate structure, identify and report all null rows before returning clean dataset.
    input: File path to ward_budget.csv (string). Expected columns: period (YYYY-MM), ward, category, budgeted_amount, actual_spend, notes.
    output: Dictionary containing: 'data' (list of valid rows), 'nulls' (list of null records with reason), 'null_count' (int), 'wards' (set), 'categories' (set). Example: {data: [...], nulls: [{'period': '2024-03', 'ward': 'Ward 2', 'category': 'Drainage & Flooding', 'reason': '...'}], null_count: 5, ...}.
    error_handling: If columns missing, raise ValueError with missing column names. If CSV malformed, flag row number and content. If period format invalid, flag specific row. If null reason (notes) empty, flag as 'REASON_NOT_PROVIDED'.

  - name: compute_growth
    description: Calculate MoM or YoY growth for a specific ward-category pair, returning per-period table with formula shown.
    input: Ward (string), Category (string), Growth_type ('MoM' or 'YoY'), dataset (from load_dataset). Example: ward='Ward 1 – Kasba', category='Roads & Pothole Repair', growth_type='MoM'.
    output: List of dicts for each period with keys: period, actual_spend, prior_period_spend, growth_pct, formula. Example: [{period: '2024-02', actual_spend: 12.2, prior_spend: 13.3, growth_pct: -8.3, formula: '(12.2-13.3)/13.3*100'}]. Null periods: {period, actual_spend: null, prior_spend, formula: 'N/A - null actual_spend', note: reason}.
    error_handling: If ward not in dataset, raise ValueError. If category not in dataset, raise ValueError. If growth_type not 'MoM' or 'YoY', raise ValueError. If only one period of data exists, return single row with growth_pct=null and formula='N/A - insufficient prior data'. If prior period null for MoM, use 'N/A - prior period null' in formula.

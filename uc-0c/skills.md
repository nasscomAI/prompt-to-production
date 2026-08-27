# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates schema, and reports null count with row identifiers before returning dataframe.
    input: "file_path (string): path to CSV. Example: '../data/budget/ward_budget.csv'"
    output: "Dictionary with keys: 'dataframe' (pandas.DataFrame), 'null_count' (int), 'null_rows' (list of dicts with period, ward, category, reason from notes column)"
    error_handling: "If file not found, raise FileNotFoundError. If required columns missing (period, ward, category, budgeted_amount, actual_spend, notes), raise ValueError with list of missing columns. Always report nulls — never silently skip them."

  - name: compute_growth
    description: Calculates month-over-month or year-over-year growth for a specific ward-category pair, returning per-period table with formulas shown.
    input: "Dictionary with keys: 'dataframe' (pandas.DataFrame), 'ward' (string), 'category' (string), 'growth_type' (string: 'MoM' or 'YoY')"
    output: "CSV-ready dataframe with columns: period, actual_spend, formula, growth_rate_pct. For null actual_spend rows: growth_rate_pct='NULL', formula='Not computed — null value'."
    error_handling: "If ward or category not found in filtered data, raise ValueError. If growth_type not 'MoM' or 'YoY', raise ValueError and ask user to specify. If all actual_spend values are null, return empty result with message 'No valid data for growth calculation'. Never aggregate across wards or categories — filter strictly."

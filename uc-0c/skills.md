skills:
  - name: load_dataset
    description: >
      Read the ward budget CSV, validate required columns, and report the count
      and details of rows with null actual_spend before returning the data.
    input: >
      input_path (str) — path to ward_budget.csv
    output: >
      tuple — (list of dict rows, list of dicts describing null rows with period, ward, category, notes)
    error_handling: >
      If file is missing, raise FileNotFoundError. If required columns (period, ward,
      category, budgeted_amount, actual_spend, notes) are missing, raise ValueError
      listing the missing columns.

  - name: compute_growth
    description: >
      Filter to a specific ward and category, compute MoM or YoY growth on
      actual_spend, and return a table with period, budgeted_amount, actual_spend,
      growth_pct, and formula_used. Null actual_spend rows are flagged, not computed.
    input: >
      rows (list of dict), ward (str), category (str), growth_type (str — "MoM" or "YoY")
    output: >
      list of dict — each with period, ward, category, budgeted_amount, actual_spend,
      growth_pct, formula_used, notes. null_flag set for rows with null actual_spend.
    error_handling: >
      If growth_type is not "MoM" or "YoY", raise ValueError.
      If ward or category not found in data, return empty list with a warning.

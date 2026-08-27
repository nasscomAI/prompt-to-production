# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads budget CSV, validates required columns, identifies and reports all null actual_spend rows before processing.
    input: "File path to ward_budget.csv"
    output: "Dict with keys: dataframe (pd.DataFrame), null_rows (list of dicts with period/ward/category/reason), metadata (dict with total_rows, null_count, wards_list, categories_list)"
    error_handling: "If file not found, raise FileNotFoundError. If required columns missing, raise ValueError with column list. If CSV is malformed, log error to stderr and attempt recovery. Report null_rows with notes explanation before returning."

  - name: compute_growth
    description: Computes MoM (Month-over-Month) or YoY (Year-over-Year) growth for specified ward and category, showing formula and handling nulls.
    input: "Dict from load_dataset, ward (string), category (string), growth_type (string: 'MoM' or 'YoY'), period_range (optional list of YYYY-MM strings)"
    output: "CSV-formatted table with columns: period, actual_spend, previous_period_spend, formula, growth_percent, null_flag (bool), notes"
    error_handling: "If ward or category not found in data, raise ValueError. If growth_type not in ['MoM', 'YoY'], raise ValueError with refusal message. If both ward AND category specified, return error if attempting cross-ward/cross-category aggregation. Mark null rows with null_flag=True and propagate notes explanation. If previous period is null in MoM, mark current row as uncomputable."

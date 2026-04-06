# skills.md

skills:
  - name: load_dataset
    description: Load budget CSV and report all null rows with their reasons before any processing.
    input: "CSV file path (string) to ward_budget.csv. Expected columns: period, ward, category, budgeted_amount, actual_spend, notes"
    output: "Dataframe with all rows loaded. Console output reports: null rows found at [period, ward, category]. Reason from notes column for each."
    error_handling: "If file not found, raise FileNotFoundError. If required columns missing, raise ValueError. If CSV is empty, raise error."

  - name: compute_growth
    description: Calculate growth rate (MoM or YoY) for a specific ward-category combination, flagging nulls.
    input: "Dataframe (from load_dataset), ward (string), category (string), growth_type (string: must be 'MoM' or 'YoY')"
    output: "CSV file with columns: period, actual_spend, growth_percent, formula, null_flag, null_reason. One row per month (12 rows total)."
    error_handling: "If ward not found in data, raise error: 'Ward not found'. If category not found, raise error: 'Category not found'. If growth_type not MoM or YoY, raise error: 'Invalid growth_type'. For first period, growth_percent is empty/dash."

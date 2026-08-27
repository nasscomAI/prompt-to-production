# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate columns, and report null actual_spend rows with their reasons before returning the data.
    input: >
      A file path to ward_budget.csv with columns: period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      A tuple of (dataframe/list of rows, null_report). The null_report is a list
      of dicts with keys: period, ward, category, reason — one entry per row where
      actual_spend is missing. The null report is printed to stdout before any
      computation begins.
    error_handling: >
      If the file does not exist, raise FileNotFoundError. If required columns
      are missing, raise ValueError naming the missing columns. If the file has
      zero data rows, raise ValueError.

  - name: compute_growth
    description: Compute per-period growth rates for a specific ward + category + growth type, with formula shown in every row and null rows flagged.
    input: >
      The loaded dataset, plus three parameters: ward (string), category (string),
      growth_type (MoM or YoY). The function filters the dataset to the specified
      ward + category before computing.
    output: >
      A CSV file with columns: period, ward, category, actual_spend,
      previous_actual_spend, growth_pct, formula, flag. For null actual_spend
      rows, growth_pct = "NULL", formula = "N/A", flag = reason from notes.
      For the first period, growth_pct = "N/A", formula = "N/A (first period)".
      All other rows show the substituted formula and rounded percentage.
    error_handling: >
      If the specified ward or category does not exist in the dataset, raise
      ValueError naming the invalid parameter. If growth_type is not MoM or YoY,
      raise ValueError. If all rows for the ward+category have null actual_spend,
      produce output with all rows flagged and a warning printed.

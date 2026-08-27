skills:
  - name: load_dataset
    description: >
      Reads the CSV file, validates column presence, counts null rows in
      actual_spend, and returns the full dataset with null row details before
      any computation begins.
    input: >
      CSV file path (string). Must be data/budget/ward_budget.csv with columns:
      period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      Dictionary containing: (1) full DataFrame, (2) total null count, (3) list
      of null rows with period, ward, category, and notes explanation.
    error_handling: >
      If file not found, raise FileNotFoundError. If columns missing, raise
      ValueError listing missing columns. If actual_spend column contains > 5
      nulls, warn user and list all null rows explicitly.

  - name: compute_growth
    description: >
      Accepts ward, category, and growth_type (MoM or YoY), filters the dataset
      to that ward and category, computes per-period growth using the requested
      formula, and returns a table with formula shown in every row.
    input: >
      Filtered DataFrame (from load_dataset), ward (string), category (string),
      growth_type (string: 'MoM' or 'YoY').
    output: >
      CSV table with columns: period, actual_spend, formula_used, growth_pct.
      If actual_spend is null, show 'NULL' and reason from notes column instead
      of growth_pct.
    error_handling: >
      If ward not in dataset, raise ValueError. If category not in dataset,
      raise ValueError. If growth_type not in ['MoM', 'YoY'], raise ValueError
      with message: "Must specify --growth-type as MoM or YoY". If all rows for
      the ward-category pair are null, return zero-row table with headers.

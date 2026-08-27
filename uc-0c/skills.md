# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports null counts and affected rows before returning data.
    input: >
      input_path (str): path to ward_budget.csv. Expected columns: period, ward,
      category, budgeted_amount, actual_spend, notes.
    output: >
      A validated dataset (list of dicts or DataFrame) along with a null report
      listing every row where actual_spend is blank — including period, ward,
      category, and the reason from the notes column.
    error_handling: >
      If the file is missing or unreadable, exit with a clear error message. If
      expected columns are missing, exit and name the missing columns. If null
      rows are found, report them immediately before any computation proceeds —
      never silently skip or fill them.

  - name: compute_growth
    description: Computes period-over-period growth for a specific ward and category, showing the formula used in every output row.
    input: >
      ward (str): the specific ward to filter on.
      category (str): the specific category to filter on.
      growth_type (str): must be explicitly provided (e.g., MoM). Never assumed.
    output: >
      A per-period table (CSV rows) with columns: period, ward, category,
      actual_spend, previous_spend, growth_percent, formula_used. Null rows
      appear with growth_percent set to "NULL — not computed" and the reason
      from the notes column.
    error_handling: >
      If --growth-type is not specified, refuse and prompt the user to specify it —
      never guess MoM or YoY. If the requested ward or category does not exist in
      the dataset, exit with an error listing valid values. If an all-ward or
      all-category aggregation is requested without explicit instruction, refuse.

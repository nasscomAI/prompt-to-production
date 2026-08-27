# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Read the ward budget CSV, validate that all required columns exist,
      and report null actual_spend rows with their reasons before
      returning the data.
    input: >
      A file path (string) to ward_budget.csv.
    output: >
      A list of dictionaries (one per row) with keys: period, ward,
      category, budgeted_amount (float), actual_spend (float or None),
      notes (string). Also prints a null report listing every row
      where actual_spend is missing, along with the reason from notes.
    error_handling: >
      If the file does not exist, raise a clear error. If required
      columns are missing, list the missing columns and exit. If
      budgeted_amount cannot be parsed as a float, flag the row.

  - name: compute_growth
    description: >
      Filter data to the specified ward and category, then compute
      period-over-period growth (MoM or YoY) with the formula shown
      in every row.
    input: >
      The full dataset (from load_dataset), plus ward (string),
      category (string), and growth_type (string: MoM or YoY).
    output: >
      A list of dictionaries with keys: period, actual_spend,
      previous_spend, formula, growth_pct, null_flag, null_reason.
      Written to a CSV file.
    error_handling: >
      If ward or category not found in data, list available values
      and exit. If growth_type is not MoM or YoY, refuse and list
      valid options. If either current or previous actual_spend is
      null, set growth_pct to NULL and include the reason.

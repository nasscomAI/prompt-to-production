# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports null count and which rows have null actual_spend before returning the data.
    input: >
      File path to ward_budget.csv.
    output: >
      A structured dataset (list of row dictionaries) with columns: period, ward,
      category, budgeted_amount, actual_spend, notes. Also prints a null report
      listing each null row with its period, ward, category, and reason from notes.
    error_handling: >
      If the file does not exist, is not a CSV, or is missing required columns
      (period, ward, category, budgeted_amount, actual_spend, notes), print an
      error and exit. Do not attempt to proceed with incomplete data.

  - name: compute_growth
    description: Takes a ward, category, and growth type, filters the dataset, and returns a per-period growth table with formula shown for each row.
    input: >
      Filtered dataset for one ward and one category, plus growth_type (MoM or YoY).
    output: >
      A CSV table with columns: period, actual_spend, formula, growth_pct, flag.
      Each row shows the spend value, the calculation formula used, the result
      rounded to 1 decimal place, and a flag column (NULL_DATA with reason if
      that period has no actual_spend, or blank if computed normally).
    error_handling: >
      If a period has null actual_spend, mark it as NULL_DATA in the flag column
      with the reason from notes. Skip growth computation for that row AND the
      following row (since previous value is missing). If ward or category not
      found, refuse and list available values.

# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null actual_spend rows with their reasons before returning the data.
    input: File path to ward_budget.csv (string).
    output: Parsed dataset (list of rows) with a null report listing each null row's period, ward, category, and reason from the notes column.
    error_handling: If the file is missing or required columns (period, ward, category, budgeted_amount, actual_spend, notes) are absent, exit with a clear error message.

  - name: compute_growth
    description: Takes a ward, category, and growth type (MoM), filters the dataset, and returns a per-period table with actual spend, growth percentage, and the formula used for each row.
    input: Ward name (string), category name (string), growth type (string, must be "MoM"), and the loaded dataset.
    output: A CSV table with columns — period, ward, category, actual_spend, previous_spend, mom_growth_pct, formula, flag. Null rows show flag with reason instead of computed growth.
    error_handling: If the ward or category is not found in the data, exit with an error. If growth type is not specified or not "MoM", refuse and prompt the user. Never interpolate or zero-fill null values.

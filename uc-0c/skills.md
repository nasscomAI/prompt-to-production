skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports null actual_spend rows and their reasons before returning the data.
    input: A CSV file containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: Validated dataset with the count and details of null actual_spend rows.
    error_handling: If the file is missing, unreadable, required columns are missing, or null rows cannot be identified, report the error and do not guess.

  - name: compute_growth
    description: Computes growth for the requested ward and category using the explicitly supplied growth type and shows the formula for each result.
    input: Validated dataset plus a ward name, category name, and growth_type such as MoM.
    output: Per-period table containing the period, actual spend, formula used, growth result, and any required null flag.
    error_handling: If ward, category, or growth_type is missing or ambiguous, refuse rather than guess; if actual_spend is null, flag the row and do not compute growth.
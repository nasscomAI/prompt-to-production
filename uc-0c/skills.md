# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads a budget CSV file, validates columns, and reports null counts and which rows have null actual_spend before returning data.
    input: >
      input_path (str): path to ward_budget.csv.
    output: >
      A tuple of (dataframe/list of dicts with all rows, null_report listing each null row with period, ward, category, and notes reason).
    error_handling: >
      If required columns are missing, raise an error listing expected vs. found columns.
      If the file cannot be read, raise an error with the file path.

  - name: compute_growth
    description: Takes a ward, category, and growth type (MoM), filters the dataset, and returns a per-period table with the formula and result shown.
    input: >
      data (list): rows from load_dataset.
      ward (str): exact ward name to filter by.
      category (str): exact category name to filter by.
      growth_type (str): "MoM" for month-over-month.
    output: >
      A CSV table with columns: period, actual_spend, previous_spend, formula, mom_growth_pct, flag.
      First period has mom_growth_pct = N/A. Null periods have flag = "NULL: [reason from notes]".
    error_handling: >
      If ward or category not found in data, raise an error listing available values.
      If growth_type is not specified or invalid, refuse and list allowed values.
      If actual_spend is null, set flag with reason and skip growth computation for that row and the following row.

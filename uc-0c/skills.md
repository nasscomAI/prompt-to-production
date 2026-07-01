# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward_budget.csv file, validates that all required columns are present, and reports the null count and which specific rows have null actual_spend values before returning the data.
    input: "csv_path (string): path to the ward_budget.csv file."
    output: "A structured dataset (list of row dictionaries) along with a null report listing each null row's period, ward, category, and reason from the notes column."
    error_handling: "If the file does not exist, raises FileNotFoundError. If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, raises ValueError listing the missing columns."

  - name: compute_growth
    description: Takes a ward name, category name, and growth type (MoM), filters the dataset to that ward+category, and returns a per-period growth table with the formula shown alongside each result.
    input: "ward (string), category (string), growth_type (string: 'MoM'), and the loaded dataset from load_dataset."
    output: "A list of row dictionaries with columns: period, actual_spend, previous_actual_spend, formula, growth_pct. Null rows are included but marked as NULL_FLAGGED with the reason from the notes column — no growth is computed for them."
    error_handling: "If ward or category is not found in the dataset, raises ValueError listing available wards/categories. If growth_type is not provided or not recognized, raises ValueError and refuses to guess — asks the user to specify."

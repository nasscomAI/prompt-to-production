# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads a ward budget CSV file, validates required columns, reports null actual_spend rows with reasons before returning the data.
    input: A string — file path to ward_budget.csv.
    output: A list of row dicts with validated columns (period, ward, category, budgeted_amount, actual_spend, notes). Prints a null report to stdout listing each null row's period, ward, category, and note reason.
    error_handling: If the file is not found, prints an error and exits. If required columns are missing, prints an error and exits. Null actual_spend values are preserved (not interpolated or dropped) and flagged in the null report.

  - name: compute_growth
    description: Filters data to a single ward + category, computes per-period growth rates (MoM or YoY) with formula shown in every row, and flags null periods.
    input: The loaded dataset (list of dicts), ward name (string), category name (string), growth type (string — "MoM" or "YoY").
    output: A list of result dicts with keys — period, actual_spend, previous_spend, growth_pct, formula, flag. Written as a CSV file.
    error_handling: If ward or category not found in data, prints an error listing valid values and exits. If growth type is not MoM or YoY, refuses and asks the user. Null actual_spend rows are output with growth_pct "NULL" and flag citing the note reason. Periods where the previous value is null also get growth_pct "NULL".

# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports null actual_spend rows with their reasons before returning the data.
    input: file_path (string — path to ward_budget.csv).
    output: A tuple of (dataframe/list of rows, null_report). The null_report is a list of dicts with period, ward, category, and notes for every row where actual_spend is blank/null. Prints null report to stdout before returning.
    error_handling: If file is missing, exit with error. If expected columns are absent, exit with error listing missing columns. If no nulls found (unexpected), print a warning since the dataset should contain 5 nulls.

  - name: compute_growth
    description: Takes a ward + category + growth_type, filters the dataset, and returns a per-period growth table with formula shown.
    input: data (list of rows from load_dataset), ward (string), category (string), growth_type (string — "MoM" or "YoY").
    output: A list of dicts with keys — period, ward, category, actual_spend, growth_type, formula, growth_pct, flag. Writes to output CSV. growth_pct is rounded to 1 decimal. Null periods are flagged, not computed.
    error_handling: If ward or category not found in data, exit with error listing valid options. If growth_type is neither MoM nor YoY, refuse and list valid options. If all periods are null for the given filter, report that no computation is possible.

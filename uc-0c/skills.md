# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports null actual_spend rows before returning the data.
    input: file_path (str) — path to ward_budget.csv.
    output: A tuple of (full dataset as list of dicts, null report as list of dicts with period/ward/category/notes). Prints null report to stdout immediately upon loading.
    error_handling: If file not found, exits with code 1. If expected columns are missing (period, ward, category, budgeted_amount, actual_spend, notes), exits with code 1 and names the missing columns.

  - name: compute_growth
    description: Takes a ward, category, and growth type, filters the dataset, and returns a per-period table with growth rates and formulas shown.
    input: dataset (list of dicts), ward (str), category (str), growth_type (str — "MoM" or "YoY").
    output: A list of dicts with columns — period, actual_spend, previous_spend, growth_pct, formula, flag. Written as CSV to the output path.
    error_handling: If ward or category not found in dataset, exits with code 1 listing available values. If growth_type is not MoM or YoY, refuses and lists valid options. Null rows produce flag="NULL — not computed" with reason from notes.

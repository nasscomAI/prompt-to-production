skills:
  - name: load_dataset
    description: Read the ward_budget.csv file, validate that all required columns are present, and report the count and identity of null actual_spend rows before returning the dataset.
    input: A file path string pointing to ward_budget.csv. The CSV must contain columns: period (YYYY-MM), ward (string), category (string), budgeted_amount (float), actual_spend (float or blank), notes (string).
    output: A structured dataset object containing all rows, plus a null_report list of dicts — each with period, ward, category, and null_reason (from the notes column) — for every row where actual_spend is blank or null.
    error_handling: If the file is not found, raise a descriptive FileNotFoundError. If any required column is missing, raise a ValueError naming the missing column. If no null rows are found, return an empty null_report with a note that all rows have values.

  - name: compute_growth
    description: Take a loaded dataset, a ward, a category, and a growth type (MoM or YoY), and return a per-period growth table with the formula shown in every row.
    input: A dataset object from load_dataset, a ward string (e.g. "Ward 1 – Kasba"), a category string (e.g. "Roads & Pothole Repair"), and a growth_type string that must be exactly "MoM" or "YoY".
    output: A CSV-compatible list of dicts with columns: period, ward, category, actual_spend, growth_pct, formula_used, null_flag. For null rows, growth_pct is "NULL_NOT_COMPUTED" and null_flag contains the reason from the notes column. For MoM, formula_used is "((current - previous) / previous) × 100". For YoY, formula_used is "((current - same_month_prior_year) / same_month_prior_year) × 100".
    error_handling: If growth_type is not "MoM" or "YoY", refuse immediately with a clear error message asking the caller to specify one — never default or guess. If the ward or category is not found in the dataset, raise a ValueError listing the valid options. If a null row is encountered, mark it NULL_NOT_COMPUTED and continue — do not skip silently.

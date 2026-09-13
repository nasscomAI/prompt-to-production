# skills.md

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates the six required columns, reports the null actual_spend count and lists exactly which rows are null before returning.
    input: Path to the CSV (e.g. ../data/budget/ward_budget.csv).
    output: List of row dicts (period, ward, category, budgeted_amount, actual_spend, notes) plus a report to stderr of total rows and every null actual_spend row with its notes reason. Never aggregates.
    error_handling: Fails with exit code 1 if the file is missing, unreadable, empty, or if any required column (period, ward, category, budgeted_amount, actual_spend, notes) is absent.

  - name: compute_growth
    description: Takes exactly one ward + one category + one growth_type (MoM or YoY) and returns a per-period growth table with the formula shown in every row.
    input: ward (exact dataset name), category (exact dataset name), growth_type (MoM or YoY). Uses data returned by load_dataset.
    output: List of per-period rows (period, ward, category, budgeted_amount, actual_spend, growth_type, formula, growth_pct, notes). Growth = (current − prior) / prior × 100, shown as e.g. "(19.7 - 14.8) / 14.8 * 100 = +33.1%". Null actual_spend rows carry a FLAGGED formula and blank growth_pct; the first period has no prior period and is N/A.
    error_handling: Refuses all-ward / cross-category aggregation and unknown ward/category/growth-type values with exit code 1 and a list of valid choices. Never guesses the growth type.

# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates its columns, and reports the null count and exact null rows before returning the data.
    input: Path to ward_budget.csv.
    output: The dataset with validated columns (period, ward, category, budgeted_amount, actual_spend, notes) plus a report listing the number of null actual_spend rows and their ward/category/period.
    error_handling: If required columns are missing, raises a clear validation error and refuses to compute. If null rows are found, reports them (count + exact rows) instead of silently dropping them.

  - name: compute_growth
    description: Computes per-ward per-category growth for the requested growth type and returns a per-period table with the formula shown.
    input: A ward name, a category name, a growth type (MoM or YoY), and the validated dataset from load_dataset.
    output: growth_output.csv — a per-ward per-category table with columns: ward, category, period, previous_value, current_value, formula, growth_percent, flag. Null rows appear with their reason from notes and flag: NULL_SKIPPED.
    error_handling: Refuses if the growth type is not specified. Refuses all-ward or all-category aggregation requests. If a period has no previous period (first month for MoM), that row is flagged rather than guessed.

# skills.md
skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports null actual_spend rows before any computation happens.
    input: file_path (str) - path to ward_budget.csv.
    output: A list of row dicts, plus a printed report of which rows have null actual_spend and their notes reason.
    error_handling: If required columns are missing, raises a clear error rather than proceeding with partial data.

  - name: compute_growth
    description: Computes period-over-period growth for exactly one ward and one category, using the specified growth type.
    input: rows (list of dicts), ward (str), category (str), growth_type (str, "MoM" or "YoY").
    output: A list of dicts per period with budgeted_amount, actual_spend, growth_pct (or blank), formula (str), and flag ("" or "NOT_COMPUTED - <reason>").
    error_handling: If ward or category is missing/ALL, or growth_type is not MoM/YoY, refuses instead of guessing or aggregating.

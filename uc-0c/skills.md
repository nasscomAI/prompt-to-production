# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports the null count and which rows are null before any computation.
    input: path (str, path to ward_budget.csv).
    output: A list of row dicts; also prints a null-row report (period, ward, category, reason) to stdout.
    error_handling: Raises a clear ValueError if required columns are missing; does not attempt to compute anything until the null report has been produced.

  - name: compute_growth
    description: Computes per-period MoM or YoY growth for one ward and one category, refusing ambiguous or missing scope.
    input: rows (list from load_dataset), ward (str), category (str), growth_type ("MoM" or "YoY").
    output: A list of per-period dicts with budgeted_amount, actual_spend, growth_type, growth_pct, flag, note (formula or reason not computed).
    error_handling: Exits with an explicit REFUSED message (not a silent default) if ward, category, or growth_type is missing/invalid, or if a prior/current period value is null.
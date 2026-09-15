# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports every null actual_spend row (period/ward/category/reason) before any computation.
    input: path to ward_budget.csv
    output: tuple (rows, null_rows) where rows is a list of dicts and null_rows is a list of (period, ward, category, notes)
    error_handling: Raises FileNotFoundError if the file is absent; raises ValueError listing missing required columns.

  - name: compute_growth
    description: Computes MoM or YoY growth as a per-period table for a single ward + category, with the formula shown on every row and null/base-missing periods flagged instead of computed.
    input: rows, ward (str), category (str), growth_type ("MoM" or "YoY")
    output: list of output-row dicts (period, ward, category, budgeted_amount, actual_spend, notes, previous_period, previous_actual_spend, formula, growth_pct, flag)
    error_handling: Refuses (ValueError) if ward/category is "ALL" or does not exist in the dataset, or if growth_type is unknown; never computes a growth value when the current or base actual_spend is null — it flags the row instead.

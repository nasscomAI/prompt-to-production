# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports null actual_spend rows before any computation.
    input: path to ward_budget.csv
    output: dict — {rows: [{period, ward, category, budgeted_amount, actual_spend, notes}], nulls: [{period, ward, category, notes}]}
    error_handling: Missing required columns or empty file → raises a clear error; rows with blank actual_spend are never dropped, they are collected into the nulls report.

  - name: compute_growth
    description: Takes a ward and category and a growth type and returns a per-period table with the growth % and formula for every row.
    input: dataset dict, ward (exact string), category (exact string), growth_type ("MoM" only)
    output: list of rows — {period, ward, category, budgeted_amount, actual_spend, growth_pct, formula, flag}
    error_handling: Ward/category not found → error, no output; null actual_spend → growth not computed, flagged with the notes reason; first period → growth "n/a — no previous period"; unsupported growth type → refuse and ask.

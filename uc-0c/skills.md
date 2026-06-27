# skills.md
# UC-0C Dataset and computation skills.

skills:
  - name: load_dataset
    description: Read the ward budget CSV and validate required columns; report null rows.
    input: Path to CSV file.
    output: Tuple (rows: list of dicts, missing_columns: list).
    error_handling: If required columns are missing, return the missing list and abort further processing.

  - name: compute_growth
    description: Compute MoM or YoY growth for a specific ward and category, preserving per-period rows and formulas.
    input: rows list (from `load_dataset`), ward string, category string, growth_type string (MoM/YoY).
    output: list of output rows including actual_spend, growth_pct, formula, null_flag, null_reason.
    error_handling: If `growth_type` is not provided, refuse (raise error). If a row has null actual_spend, mark it and do not compute growth for that row.

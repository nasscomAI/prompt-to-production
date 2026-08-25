# skills.md

skills:
  - name: load_dataset
    description: Read the budget CSV, validate expected columns, and report null count + which rows before returning any data.
    input: file_path (str, path to ward_budget.csv).
    output: list of dict rows (period, ward, category, budgeted_amount, actual_spend or None, notes); prints null row count + each null row's period/ward/category/notes to stdout before returning.
    error_handling: If a required column is missing from the header, raise immediately with the missing column name — never silently proceed with a partial schema.

  - name: compute_growth
    description: Given ward, category, and growth_type (MoM or YoY), return a per-period table with the formula shown for each computed value, flagging null rows instead of computing them.
    input: rows (list from load_dataset), ward (str), category (str), growth_type (str, "MoM" or "YoY").
    output: list of dict rows {period, actual_spend, formula, growth_percent} — growth_percent is "NA" and formula is "not computed" for null/first-period rows.
    error_handling: If ward, category, or growth_type is missing/blank/"ALL", raise a refusal (not a silent default) with a message naming exactly which parameter must be specified.

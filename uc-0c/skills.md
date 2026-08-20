# skills.md

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, and reports the null count plus exactly which rows have null actual_spend before any computation.
    input: input_path (str) — path to the CSV
    output: tuple (rows list of dicts, null_rows list of dicts with period/ward/category/notes)
    error_handling: Raises SystemExit with a clear message if the file is missing or a required column is absent; a missing/non-numeric actual_spend is treated as null and reported.

  - name: compute_growth
    description: Takes a ward + category + growth type and returns a per-period table for that single pair with actual spend, previous-period spend, growth percentage and the formula shown on every row.
    input: rows (list of dicts), ward (str), category (str), growth_type (str)
    output: list of dicts with columns period, ward, category, budgeted_amount, actual_spend, previous_period_actual_spend, growth_type, growth_pct, formula, flag, notes
    error_handling: Null rows are flagged NULL_ACTUAL_SPEND with the notes reason; months with no previous month return growth N/A rather than a fabricated number.
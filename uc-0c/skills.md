# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates columns, reports null count and which rows before returning structured data
    input: csv_path — path to ward_budget.csv file
    output: dict with keys: columns (list), rows (list of dicts), null_count (int), null_rows (list of ints), notes (dict mapping row_idx -> note_text)
    error_handling: If file not found or columns missing, raise ValueError with clear message. If null actual_spend rows found, report count and row indices without failing.
    error_handling_ambiguous: Reports null findings transparently; does not guess or impute values.

  - name: compute_growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown
    input: ward — string (e.g. "Ward 1 – Kasba"), category — string (e.g. "Roads & Pothole Repair"), growth_type — "MoM" or "YoY"
    output: list of dicts with keys: period, actual_spend, previous_period_spend, formula, growth_value_pct. Each row shows the computation formula and percentage change. Null rows include flag: "null" and reason from notes.
    error_handling: If ward/category not found in dataset, raise ValueError listing available wards/categories. If growth_type not "MoM" or "YoY", raise ValueError. If actual_spend is null, growth_value_pct is null and formula reports "null — no data".
    error_handling_ambiguous: Refuses to compute if inputs not found; does not blend across wards/categories.

# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its columns, and reports null actual_spend rows before returning data.
    input: one string — path to ward_budget.csv, as passed via --input CLI argument.
    output: dict — {"rows": list of row dicts (period, ward, category, budgeted_amount: float, actual_spend: float or None, notes: str), "null_report": {"count": int, "rows": [{"period", "ward", "category", "reason"}]}}.
    error_handling: Missing/unreadable file → exit early with a clear error and write no output. Missing or misspelled required column → error listing found vs expected columns. Non-numeric budgeted_amount/actual_spend → reported as a bad row with line number; a non-numeric value is treated as null only if blank, otherwise it fails validation.

  - name: compute_growth
    description: Computes per-period spend growth for one ward + one category with the formula shown on every row.
    input: dataset dict from load_dataset, plus ward (str), category (str), growth_type (str — "MoM" compares previous month, "YoY" compares same month prior year).
    output: None returned — writes growth_output.csv with header period,ward,category,current_spend,base_spend,growth_pct,formula,flag and one row per available period in chronological order; prints completion status including null count.
    error_handling: Ward/category not found in dataset → refuse with the list of valid values, no output written. growth_type missing or not MoM/YoY → refuse and ask, never default. Null current or base spend → row emitted with empty numeric fields, flag NOT_COMPUTED, and the notes-column reason quoted verbatim; such rows are never dropped, zero-filled, or interpolated.

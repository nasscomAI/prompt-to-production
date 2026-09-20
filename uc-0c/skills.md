skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null actual_spend rows before any growth is computed.
    input: "input_path (string path to ward_budget.csv with columns period, ward, category, budgeted_amount, actual_spend, notes)."
    output: "A list of row dicts plus a null report: null_count and a list of {period, ward, category, notes} for every blank actual_spend."
    error_handling: "If the file is missing or required columns are absent, raise a clear error and do not compute growth. Blank actual_spend is recorded in the null report and kept in the dataset — never silently dropped. Invalid numeric spend is treated as null and flagged."

  - name: compute_growth
    description: Computes the requested growth type for one ward and one category, returning a per-period table with formula shown.
    input: "Loaded rows; ward (exact string, e.g. 'Ward 1 – Kasba'); category (exact string, e.g. 'Roads & Pothole Repair'); growth_type (required string, e.g. MoM); output_path (string path to growth_output.csv)."
    output: "A CSV with one row per period for that ward and category: period, ward, category, actual_spend, previous_spend, growth_pct, formula, null_flag, null_reason."
    error_handling: "If growth_type is missing, refuse and ask the user to specify it. If ward or category is missing or requests all-ward aggregation, refuse. If a period has null actual_spend, write the row with growth_pct blank, null_flag NULL, and null_reason from notes — do not compute. If the ward+category pair has no rows, refuse with a not-found message."

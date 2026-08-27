skills:
  - name: load_dataset
    description: Reads the budget CSV, validates schema, and reports all null actual_spend rows with reasons before analysis.
    input: "input_path: string path to CSV containing period, ward, category, budgeted_amount, actual_spend, notes."
    output: "dict with rows (list), null_count (int), null_rows (list of period/ward/category/notes), wards (list), categories (list)."
    error_handling: "Refuse with explicit error if file is missing, required columns are absent, or CSV cannot be parsed."

  - name: compute_growth
    description: Computes per-period growth for one ward and one category using explicit growth_type and includes formula per row.
    input: "rows: list from load_dataset; ward: string; category: string; growth_type: one of MoM or YoY."
    output: "list of rows with period, ward, category, actual_spend, growth_type, formula, growth_pct, status, null_reason."
    error_handling: "Refuse if ward/category imply aggregation (Any/All/missing), growth_type missing/unsupported, or no matching records."

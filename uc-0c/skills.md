# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports nulls before returning rows.
    input: File path (string) to ward_budget.csv with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: A list of row dicts plus a null report (count and the period/ward/category/notes of each null actual_spend row) printed to stdout.
    error_handling: Raises FileNotFoundError if the file is missing and ValueError if required columns are absent. Never drops null rows silently — they are kept and reported.

  - name: compute_growth
    description: Computes per-period MoM or YoY growth for one ward plus one category with the formula shown.
    input: Filtered rows (single ward + single category, sorted by period) and growth_type (MoM or YoY).
    output: A per-period table (list of dicts) with period, ward, category, budgeted_amount, actual_spend, prev_actual_spend, growth_pct, formula, and note — null-affected rows flagged, never computed.
    error_handling: Refuses (raises ValueError) if ward/category is missing or requests all-ward/all-category aggregation. Refuses if growth_type is missing or unsupported instead of guessing.

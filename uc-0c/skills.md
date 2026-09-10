# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null actual_spend rows before returning data.
    input: `input_path` (path to a CSV with period, ward, category, budgeted_amount, actual_spend, notes columns).
    output: The parsed row list plus a null report (count and per-row period, ward, category, and notes reason) printed to stdout.
    error_handling: Raises a clear refusal error if the file is missing or required columns are absent; never proceeds with the wrong schema.

  - name: compute_growth
    description: Computes per-period growth for one ward plus one category with the formula shown and nulls flagged.
    input: Row list plus `ward` (exact ward string), `category` (exact category string), and `growth_type` (MoM or YoY only).
    output: Per-period table rows with period, ward, category, budgeted_amount, actual_spend, growth_pct, formula, and flag columns, in chronological order.
    error_handling: Refuses (no guessing) when ward, category, or growth_type is missing, names no data, or requests cross-ward/category aggregation; null or incomputable growth cells are left blank with a flag reason, never zero-filled.

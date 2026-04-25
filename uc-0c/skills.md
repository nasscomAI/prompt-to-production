skills:
  - name: load_dataset
    description: Reads ward budget CSV, validates schema, and reports null actual_spend rows before any computation.
    input: >
      csv_path (string path) to ward_budget.csv containing columns:
      period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      Object with:
      - dataset (validated table)
      - row_count
      - null_actual_spend_count
      - null_rows: list of {period, ward, category, notes}
      - validation_status ("ok" | "error")
    error_handling: >
      Return validation_status="error" with a concrete message when file cannot be read,
      required columns are missing, period format is invalid, or types are incompatible.
      Do not continue to compute metrics on invalid input.

  - name: compute_growth
    description: Computes per-period growth for one ward and one category using an explicit growth_type and formula.
    input: >
      dataset (from load_dataset), ward (string), category (string),
      growth_type (enum: MoM or YoY).
    output: >
      Per-period table for the selected ward + category including:
      period, actual_spend, growth_value, growth_type, formula, status, note.
      status is "computed" or "skipped_null".
    error_handling: >
      Refuse when growth_type is missing/invalid, ward or category are missing/unknown,
      or request implies cross-ward/cross-category aggregation. For null actual_spend rows,
      set status="skipped_null", keep growth_value empty, and surface notes as the reason.

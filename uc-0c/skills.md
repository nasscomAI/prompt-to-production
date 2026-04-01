# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and returns structured rows with explicit null diagnostics before any computation.
    input: >
      input_path: string path to ward_budget.csv.
      Required columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      Structured dataset object with:
      rows (ordered records),
      distinct_wards,
      distinct_categories,
      null_rows list [{period, ward, category, notes}],
      and null_count.
      Must preserve source order and raw values for traceability.
    error_handling: >
      If file is unreadable, return a clear file-path error.
      If required columns are missing, return a schema validation error listing missing column names.
      Never auto-fill null actual_spend values; report them explicitly.

  - name: compute_growth
    description: Computes growth for a single ward and single category using an explicit growth type and returns a per-period table with formula shown per row.
    input: >
      dataset object from load_dataset,
      ward (string),
      category (string),
      growth_type (string, required: MoM or YoY).
    output: >
      Per-period result table with columns including:
      period,
      ward,
      category,
      actual_spend,
      growth_type,
      formula,
      growth_percent,
      status.
      Rows with null current or required comparison value must be status=FLAGGED_NULL and not numerically computed.
    error_handling: >
      Refuse if growth_type is missing or unsupported.
      Refuse if ward/category filter is absent, mixed, or requests all-ward aggregation.
      If prior-period comparator is unavailable or zero, output status=NOT_COMPUTABLE with reason instead of guessing.

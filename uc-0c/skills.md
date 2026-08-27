skills:
  - name: load_dataset
    description: Reads the CSV, validates required schema, and reports null actual_spend rows before any computation.
    input: >
      CSV file path (string). Expected columns: period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      Structured dataset plus a validation report containing row count, distinct
      ward/category counts, null actual_spend count, and the exact null rows with
      period, ward, category, and notes.
    error_handling: >
      If file is missing, unreadable, or required columns are absent, return a
      validation error and stop. If nulls exist, do not fail; return them as
      flagged rows that downstream skills must honor.

  - name: compute_growth
    description: Computes per-period growth for one ward and one category using an explicit growth_type, with formula shown for each computed row.
    input: >
      Validated dataset object, ward (string), category (string), growth_type
      (enum: MoM or YoY), and optional output path.
    output: >
      Per-period table for the selected ward/category with columns: period,
      actual_spend, growth_value, growth_type, formula_used, and status
      (computed or null_flagged_with_reason).
    error_handling: >
      Refuse if growth_type is missing or unsupported, or if ward/category are
      missing or ambiguous. Refuse requests that aggregate across wards or
      categories unless explicitly instructed. For rows with null actual_spend,
      return status as null_flagged_with_reason and skip growth computation.

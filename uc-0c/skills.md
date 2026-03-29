skills:
  - name: load_dataset
    description: Reads ward budget CSV, validates required schema, and reports all null actual_spend rows before any computation.
    input: "CSV file path with columns: period, ward, category, budgeted_amount, actual_spend, notes."
    output: "Validated tabular dataset plus null report containing null count and row details (period, ward, category, notes)."
    error_handling: "If file is missing/unreadable or required columns are absent, raise a validation error and stop. If period format or numeric fields are invalid, return explicit row-level validation errors and refuse computation."

  - name: compute_growth
    description: Computes per-period growth for exactly one ward and one category using an explicitly provided growth_type and emits formula per row.
    input: "Validated dataset + ward + category + growth_type (MoM or YoY)."
    output: "Per-period table for the selected ward/category with actual_spend, growth_result, formula_used, and status/flag columns."
    error_handling: "If growth_type is missing/unsupported, refuse and request explicit valid value. If ward/category filter implies aggregation or not found, return refusal/validation error. If current/prior value is null or denominator is zero, mark row as not computed with explicit reason and include notes context."
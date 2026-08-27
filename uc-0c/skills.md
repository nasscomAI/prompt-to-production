skills:
  - name: load_dataset
    description: Reads the budget CSV, validates schema, and reports null rows before any growth computation.
    input: "input_path: string path to ward_budget.csv (UTF-8 CSV with required columns)."
    output: "object with validated rows, schema status, null_count, and null_rows list (period, ward, category, notes)."
    error_handling: "If file is missing/unreadable, CSV malformed, or required columns are absent, return a clear validation error and stop; do not continue with partial schema."

  - name: compute_growth
    description: Computes per-period growth for the specified ward and category using the explicit growth_type and returns formula-visible results.
    input: "validated dataset object + ward (string) + category (string) + growth_type (string, required, e.g., MoM) + optional output path."
    output: "per-period table for only the requested ward-category, including period, actual_spend, growth_value, formula_used, null_flag, and null_reason."
    error_handling: "If growth_type is missing/unknown, refuse and request clarification; if target ward/category is not found, return scoped error; if actual_spend is null for a row, flag it with notes reason and skip numeric computation for that row; refuse requests that imply all-ward/all-category aggregation unless explicitly instructed."

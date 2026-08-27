skills:
  - name: load_dataset
    description: Reads budget CSV, validates schema, and detects null actual_spend rows.
    input: input_path string.
    output: tuple(rows, null_rows) where each item is a list of dictionaries.
    error_handling: Raises validation error for missing required columns or empty header.

  - name: compute_growth
    description: Computes MoM or YoY growth for one ward and one category with formula trace.
    input: rows list plus ward, category, and growth_type.
    output: list of per-period result rows including status and growth percent.
    error_handling: Raises clear errors for invalid growth_type or missing scoped rows; flags null/zero baseline rows without crashing.

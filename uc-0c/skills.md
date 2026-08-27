# skills.md
skills:
  - name: load_dataset
    description: Reads ward budget CSV input, validates schema, and identifies null actual_spend rows before analysis.
    input: Path to ward_budget.csv with required columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: Parsed rows with typed numeric fields plus a null-row report containing period, ward, category, and notes reason.
    error_handling: If required columns are missing or values are malformed, stop with a clear validation error and do not compute growth.

  - name: compute_growth
    description: Computes growth for one ward and one category using the requested growth_type and emits an auditable per-period table.
    input: Parsed dataset rows, ward, category, and growth_type (MoM or YoY).
    output: Per-period output rows including prior-period value, growth result, formula string, and null/status flags.
    error_handling: Refuse all-ward or all-category scope, refuse missing growth_type, and mark rows as not computed when current or base period values are null/invalid.

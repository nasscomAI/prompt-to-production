skills:
  - name: load_dataset
    description: Loads ward budget CSV data, validates required columns, and reports null actual_spend rows with notes.
    input: CSV file path string.
    output: Tuple of parsed row list and null-row list with period/ward/category/notes.
    error_handling: Raises explicit validation errors for missing headers or missing required columns.

  - name: compute_growth
    description: Computes period-level growth for a specific ward and category using explicit MoM or YoY logic.
    input: Parsed dataset rows plus ward, category, and growth_type.
    output: Per-period output table containing actual spend, growth percent, formula, status, and null reason.
    error_handling: Refuses missing/invalid growth_type, refuses missing ward/category scope, and flags null/base-value issues instead of silently computing.

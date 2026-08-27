skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null actual_spend rows before any computation.
    input: CSV file path (expected ../data/budget/ward_budget.csv).
    output: Structured dataset records plus validation metadata including row count, column check status, null count, and null row details with notes.
    error_handling: If file is unreadable or required columns are missing, return a validation failure with explicit missing elements and stop downstream compute requests.

  - name: compute_growth
    description: Computes period-level growth for one ward and one category using an explicit growth_type and returns formula-annotated results.
    input: Dataset records plus ward string, category string, and required growth_type (MoM or YoY).
    output: Per-period table for the specified ward-category with actual_spend, growth_value, formula_used, and null flags where computation is not possible.
    error_handling: Refuse if growth_type is not provided, if ward/category scope is missing, or if input implies cross-ward/category aggregation; flag null periods with notes and skip growth computation for those rows.

# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports null actual_spend rows before returning structured data.
    input: CSV file path containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: Validated dataset plus null diagnostics including null count and row-level details (period, ward, category, notes).
    error_handling: If required columns are missing or file cannot be read, return a hard error and stop. If null actual_spend rows are found, surface them explicitly for downstream flagging rather than imputing values.

  - name: compute_growth
    description: Computes growth for a specified ward, category, and growth_type, returning a per-period output table with formulas shown.
    input: Validated dataset from load_dataset and parameters ward, category, growth_type (MoM or YoY).
    output: Per-period table for the selected ward and category including actual_spend, growth result, formula string, and null flags where computation is not possible.
    error_handling: If growth_type is missing, refuse and request explicit selection. If request implies cross-ward or cross-category aggregation without explicit instruction, refuse. If period has null actual_spend (current or required previous/reference period), flag row and do not compute growth.

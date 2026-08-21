# skills.md

skills:
  - name: load_dataset
    description: Reads and validates the budget CSV, reports null count and affected rows before returning the dataset.
    input: File path to ward_budget.csv (string); expected columns — period, ward, category, budgeted_amount, actual_spend, notes.
    output: Validated pandas DataFrame; console report listing all null actual_spend rows with their reason from notes column.
    error_handling: If columns are missing or data types invalid, raise error with column list. Report exact null row count and locations before processing.

  - name: compute_growth
    description: Computes per-period growth metrics (MoM or YoY) for a specified ward and category, with formulas displayed.
    input: DataFrame (from load_dataset), ward name (string), category name (string), growth_type (enum — MoM or YoY).
    output: Per-period table with columns — period, actual_spend, growth_pct, formula; null rows marked as NULL with reason appended.
    error_handling: If growth_type is missing or ambiguous, refuse and ask user to specify. If ward or category not found, report exact values present. Return NULL flag with reason for rows with missing actual_spend.

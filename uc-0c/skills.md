# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports null actual_spend rows before any computation.
    input: CSV path containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: List of CSV row dictionaries; console report with total rows, null count, and each null row's period, ward, category, and notes reason.
    error_handling: Refuses missing files and files without all required columns.

  - name: compute_growth
    description: Computes growth for one explicit ward and category using the requested growth type, returning one row per period with the formula shown.
    input: Dataset rows, exact ward string, exact category string, and explicit growth_type.
    output: Per-period table with ward, category, period, budgeted_amount, actual_spend, growth_type, growth, formula, status, and notes.
    error_handling: Refuses missing ward, missing category, missing growth_type, unsupported growth types, and ward/category pairs with no rows; flags null actual_spend rows instead of computing growth for them.

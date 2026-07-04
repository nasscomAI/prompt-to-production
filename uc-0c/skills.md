# skills.md

skills:
  - name: load_dataset
    description: Load the budget CSV, validate the required columns, and report null rows before any growth computation.
    input: A CSV file path and the expected column names for period, ward, category, budgeted_amount, actual_spend, and notes.
    output: A parsed dataset object with metadata about the file, column validation, null counts, and the exact rows where actual_spend is blank.
    error_handling: If required columns are missing or the file cannot be read, stop and report the problem; if null values are present, surface them with their notes rather than silently dropping them.

  - name: compute_growth
    description: Compute growth for one ward and one category using the requested growth type and return a per-period table.
    input: A dataset object, a ward name, a category name, and a growth type such as MoM or YoY.
    output: A per-period table with period, ward, category, actual_spend, growth_value, formula, and null_flag where applicable.
    error_handling: If the request is ambiguous, would require aggregation across multiple wards or categories, or lacks a growth type, refuse and request clarification; if actual_spend is null, flag the row and do not compute growth for it.

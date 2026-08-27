# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports null actual_spend rows before any computation.
    input: Path to ward_budget.csv.
    output: A dict with 'rows' (list of dicts) and 'nulls' (list of rows where actual_spend is blank, with their notes).
    error_handling: >
      Raises ValueError if required columns (period, ward, category, budgeted_amount,
      actual_spend) are missing. Reports the null count and which rows are null up
      front so downstream steps never silently compute on missing data.

  - name: compute_growth
    description: Computes a per-period growth table for one ward + category + growth_type, showing the formula and flagging nulls.
    input: The loaded dataset, a ward string, a category string, and a growth_type ("MoM" or "YoY").
    output: A CSV-compatible list of per-period records: period, budgeted_amount, actual_spend, formula, growth_pct (or NULL + note).
    error_handling: >
      If ward/category combination has no rows, returns an empty table with a warning.
      If growth_type is missing or invalid, raises a refusal error. Null periods are
      emitted as rows with growth "NULL" and the notes reason, never imputed.

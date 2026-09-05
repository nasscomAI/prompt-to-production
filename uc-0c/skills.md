# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates its columns, and reports null rows before any computation.
    input: A file path to ward_budget.csv (columns: period, ward, category, budgeted_amount, actual_spend, notes).
    output: The dataset rows plus a report of the null count and the exact list of null rows (period/ward/category) with their notes reason.
    error_handling: If required columns are missing, raises a clear error. If actual_spend is blank, records that row as null with its notes reason rather than discarding or imputing it.

  - name: compute_growth
    description: Produces a per-month growth table for one ward and category with the formula shown, flagging null rows.
    input: The loaded dataset, one ward name, one category name, and a growth_type (MoM or YoY).
    output: A per-period table (one row per month) with columns period, actual_spend, formula, growth_type, growth_result, null_reason.
    error_handling: Refuses (returns an error, no table) if growth_type is missing or if more than one ward/category is requested. For any null actual_spend row, outputs a flagged row with the notes reason and blank growth result instead of computing.
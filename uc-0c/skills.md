# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, reports the null count and which specific rows have null actual_spend before returning the dataset.
    input: >
      A single file path (string) to the ward budget CSV.
      Example: file_path="../data/budget/ward_budget.csv"
    output: >
      A dict with two keys:
        rows      — list of row dicts with keys: period, ward, category,
                    budgeted_amount, actual_spend (float or None), notes
        null_rows — list of row dicts where actual_spend is null, each including
                    the notes column explaining why
      Prints to stdout before returning: total rows loaded, null count, and the
      period+ward+category of every null row.
      Example: {"rows": [...], "null_rows": [{"period": "2024-03", "ward": "Ward 2...", ...}]}
    error_handling: >
      If file_path does not exist, raise FileNotFoundError with a clear message.
      If any of the required columns (period, ward, category, budgeted_amount,
      actual_spend, notes) are missing, raise ValueError naming every missing column.
      Never silently skip null rows or substitute zero for null actual_spend values.

  - name: compute_growth
    description: Takes a ward, category, and growth_type, filters the dataset to that exact slice, flags null rows, and returns a per-period growth table with the formula shown in every row.
    input: >
      Four arguments:
        rows        — full dataset as returned by load_dataset (list of row dicts)
        ward        — exact ward name string (e.g. "Ward 1 – Kasba")
        category    — exact category name string (e.g. "Roads & Pothole Repair")
        growth_type — must be explicitly provided as "MoM" or "YoY" — no default
      Example: compute_growth(rows, ward="Ward 1 – Kasba",
                              category="Roads & Pothole Repair", growth_type="MoM")
    output: >
      A list of period-result dicts, each with:
        period       — YYYY-MM string
        actual_spend — float or None
        growth_value — float (percentage) or None if row or prior period is null
        formula_used — string showing the exact calculation
                       e.g. "MoM = (19.7 - 14.8) / 14.8 * 100 = +33.1%"
        null_flag    — "NULL: <reason from notes>" or "" (blank)
      Example: [{"period": "2024-07", "actual_spend": 19.7, "growth_value": 33.1,
                 "formula_used": "MoM = (19.7 - 14.8) / 14.8 * 100 = +33.1%", "null_flag": ""}]
    error_handling: >
      If growth_type is not provided or is not exactly "MoM" or "YoY", raise ValueError
      and prompt the user to specify — never silently default to either type.
      If ward or category produce an empty slice (no matching rows), raise ValueError
      naming the unmatched ward/category — never return an empty table silently.
      If a row has null actual_spend, set growth_value to None and populate null_flag
      with the reason from the notes column — do not compute growth through a null row.

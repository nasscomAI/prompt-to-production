# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the budget CSV, validates its columns, and reports the count and identity
      of every null actual_spend row before any computation happens.
    input: >
      str — path to ward_budget.csv.
    output: >
      dict — {rows: list of row dicts, null_rows: list of (period, ward, category, notes)
      for every row with missing actual_spend, column_report: validation of expected columns}.
    error_handling: >
      Raises a clear error if required columns (period, ward, category, budgeted_amount,
      actual_spend, notes) are missing; never silently drops null rows — they are always
      reported in null_rows.

  - name: compute_growth
    description: >
      Takes a ward + category + growth type and returns a per-period table with the
      formula shown and nulls flagged, never aggregated beyond the requested scope.
    input: >
      dataset (output of load_dataset), ward (str), category (str), growth_type (str:
      "MoM" or "YoY").
    output: >
      list of row dicts — {period, actual_spend, growth_value, formula, flag, flag_reason}
      for the requested ward + category only.
    error_handling: >
      If growth_type is None or invalid, refuses with an error asking for MoM or YoY —
      never guesses. If a period in scope has a null actual_spend, the row is included
      with flag set and the reason from notes; growth is not computed for that row.
      If asked to aggregate beyond ward + category, refuses.
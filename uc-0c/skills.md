skills:
  - name: load_dataset
    description: >
      Read the ward budget CSV, validate required columns exist,
      report the count and details of null actual_spend rows before
      returning the data.
    input: >
      String: path to ward_budget.csv.
    output: >
      Tuple of (list[dict] rows, list[dict] null_rows) where each
      null_row has period, ward, category, and notes.
    error_handling: >
      If file not found or missing required columns (period, ward,
      category, budgeted_amount, actual_spend, notes), raise a
      clear ValueError.

  - name: compute_growth
    description: >
      Given a ward, category, and growth type (MoM), filter the
      dataset to matching rows, sort by period, and compute the
      growth percentage. Rows with null actual_spend are flagged
      rather than computed.
    input: >
      list[dict] rows, string ward, string category, string growth_type.
    output: >
      list[dict] output rows with fields: period, actual_spend,
      previous_spend, growth_pct, formula, null_flag (reason or empty).
    error_handling: >
      If growth_type is not 'MoM', raise ValueError. If fewer than
      2 periods have non-null data, set growth_pct to 'N/A' with
      a note explaining insufficient data.

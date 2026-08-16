skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate columns, and report every null actual_spend row before any growth is computed.
    input: >
      input_path (str) to ward_budget.csv. Required columns: period, ward,
      category, budgeted_amount, actual_spend, notes.
    output: >
      A dict with rows (list of parsed row dicts), null_report (list of
      {period, ward, category, notes} for blank actual_spend), and
      null_count (int). actual_spend is float or None.
    error_handling: >
      Missing file → FileNotFoundError. Missing required column → ValueError
      naming the column. Blank actual_spend is not an error; it is recorded
      in null_report and kept as None. Never coerce null to 0.

  - name: compute_growth
    description: Compute per-period growth for exactly one ward and one category, showing the formula on every row.
    input: >
      dataset dict from load_dataset, ward (str), category (str),
      growth_type (str: MoM or YoY).
    output: >
      A list of row dicts for growth_output.csv with fields period, ward,
      category, actual_spend, growth_pct, formula, status, notes.
      status is COMPUTED, NO_PRIOR, NULL_FLAGGED, or NOT_COMPUTED.
    error_handling: >
      Missing/all ward or category → raise RefusalError with allowed values.
      Unknown growth_type → raise RefusalError listing MoM and YoY.
      Null or missing prior actual → no numeric growth; status explains why.

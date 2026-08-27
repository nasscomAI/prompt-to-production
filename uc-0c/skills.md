# skills.md

skills:
  - name: load_dataset
    description: >
      Read the ward budget CSV, validate columns, and report null count
      with row details before returning the data.
    input: |
      file_path (str) — path to ward_budget.csv.
    output: |
      list[dict] — parsed CSV rows. Also prints null report to stderr
      showing count and list of (period, ward, category, notes) for each
      null actual_spend row.
    error_handling: >
      If required columns (period, ward, category, budgeted_amount,
      actual_spend, notes) are missing, raise ValueError listing missing
      columns. If file is not found, raise FileNotFoundError.

  - name: compute_growth
    description: >
      Filter data to the given ward and category, sort by period, then
      compute MoM or YoY growth on actual_spend. Rows with null
      actual_spend produce a flagged result instead of a computed value.
    input: |
      data (list[dict]) — parsed CSV rows.
      ward (str) — exact ward name to filter by.
      category (str) — exact category name to filter by.
      growth_type (str) — "MoM" or "YoY".
    output: |
      list[dict] — output rows with keys: period, ward, category,
      actual_spend, prev_actual_spend, growth_value, formula, flag.
      Null actual_spend rows have growth_value = "N/A" and
      flag = notes text.
    error_handling: >
      If ward or category not found in data, raise ValueError. If
      growth_type is not "MoM" or "YoY", raise ValueError.

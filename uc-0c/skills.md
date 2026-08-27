skills:
  - name: load_dataset
    description: >
      Read the ward budget CSV, validate required columns (period, ward,
      category, budgeted_amount, actual_spend, notes), and report the count
      and details of rows with null actual_spend before returning.
    input: >
      string — file path to a CSV with columns: period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      dict with keys: "data" (list of row dicts), "null_rows" (list of dicts
      with period, ward, category, and notes for each null actual_spend row).
    error_handling: >
      If the file cannot be read or required columns are missing, raise a
      clear error. If the CSV is empty, return empty data and null_rows lists.

  - name: compute_growth
    description: >
      Compute growth (MoM or YoY) for a specific ward and category across all
      periods, returning a table with actual_spend, growth percentage, and the
      formula used for each row. Rows with null actual_spend are flagged
      instead of computed.
    input: >
      data — list of row dicts from load_dataset. ward — string. category —
      string. growth_type — "MoM" or "YoY".
    output: >
      list of dicts — each with keys: period, ward, category, actual_spend,
      growth, formula, null_flag (if applicable). The growth column shows the
      computed percentage or "N/A (null)".
    error_handling: >
      If ward or category is not found in the data, raise a clear error.
      If growth_type is not "MoM" or "YoY", raise an error asking the user
      to specify. If a row has null actual_spend, set growth to "N/A" and
      null_flag to the notes reason instead of computing.

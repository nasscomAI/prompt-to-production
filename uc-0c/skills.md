# skills.md — UC-0C Skills

skills:
  - name: load_dataset
    description: >
      Reads a ward budget CSV, validates required columns, reports count of null
      actual_spend rows and their period/ward/category/notes before returning the
      DataFrame.
    input: >
      file_path (str) — absolute or relative path to a CSV with columns:
      period, ward, category, budgeted_amount, actual_spend, notes
    output: >
      pandas.DataFrame with all columns preserved. Prints null-row details to
      stdout before returning.
    error_handling: >
      If file not found — raise FileNotFoundError. If required columns missing —
      raise ValueError listing which columns are absent. If CSV is empty — raise
      ValueError.

  - name: compute_growth
    description: >
      Computes per-period growth (MoM or YoY) for a single ward + category
      combination. Adds a column showing the formula used for each row. Rows with
      null actual_spend are excluded from growth calculation and flagged in output.
    input: >
      df (pandas.DataFrame) — loaded dataset; ward (str); category (str);
      growth_type (str, one of "MoM" or "YoY")
    output: >
      pandas.DataFrame with columns: period, ward, category, actual_spend,
      growth_rate, formula. Growth rate is None for rows where either current or
      prior-period actual_spend is null.
    error_handling: >
      If growth_type not in ["MoM", "YoY"] — raise ValueError. If ward not in
      df["ward"] — raise ValueError listing available wards. If category not in
      df["category"] — raise ValueError listing available categories.

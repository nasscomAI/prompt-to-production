# skills.md — UC-0C: Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads a ward budget CSV file, validates required columns, reports null
      count and which rows contain nulls before returning structured data.
    input: File path (string) to a CSV with columns: period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      A dictionary with keys: "data" (list of row dicts), "nulls" (list of
      dicts with row details and null reason), "summary" (dict with total_rows,
      null_count, wards, categories).
    error_handling: >
      If the file does not exist, raise FileNotFoundError. If required columns
      are missing, raise ValueError listing the missing columns. If the file is
      empty, raise ValueError.

  - name: compute_growth
    description: >
      Takes ward + category + growth_type and returns a per-period table
      showing actual_spend, growth percentage, and formula used for each month.
    input: >
      A dictionary of structured data (output of load_dataset), ward name
      (string), category name (string), growth_type ("MoM" or "YoY").
    output: >
      A list of dicts with keys: period, actual_spend, prev_spend, growth_pct,
      formula, is_null, null_reason. Null rows appear first, flagged but not
      computed.
    error_handling: >
      If the ward or category is not found in the data, raise KeyError. If
      growth_type is not "MoM" or "YoY", raise ValueError. If the dataset
      has fewer than 2 periods for the selected ward/category, raise ValueError.

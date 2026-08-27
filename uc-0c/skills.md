skills:
  - name: load_dataset
    description: >
      Read the ward budget CSV, validate expected columns exist, report total
      rows and count of null actual_spend values with their period/ward/category
      and reason before returning the data.
    input: >
      Path to a CSV file with columns: period, ward, category, budgeted_amount,
      actual_spend, notes.
    output: >
      A list of row dicts. Null actual_spend values are preserved as None with
      the reason available in the notes field.
    error_handling: >
      If the file does not exist, raise FileNotFoundError. If required columns
      are missing, raise ValueError listing the missing columns. If the file is
      empty, return an empty list.

  - name: compute_growth
    description: >
      Filter dataset to a specific ward and category, then compute growth
      (MoM or YoY) per period. Each output row includes the formula used.
    input: >
      rows (list of dicts), ward (str), category (str), growth_type (str:
      "MoM" or "YoY").
    output: >
      A list of dicts with keys: period, actual_spend, growth_pct, formula,
      null_flag, null_reason. Rows with null actual_spend are included with
      null_flag = TRUE and growth_pct left blank.
    error_handling: >
      If ward or category has no matching data, return an empty list with a
      warning. If growth_type is not MoM or YoY, raise ValueError.

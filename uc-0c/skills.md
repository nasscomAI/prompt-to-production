# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads CSV file, validates required columns, identifies and reports all null actual_spend rows before returning the dataset.
    input: |
      csv_file_path (string)
      Expected columns: period (YYYY-MM), ward (string), category (string), budgeted_amount (float), actual_spend (float or null), notes (string)
    output: |
      dict with keys: {rows, null_count, null_details}
      - rows: list of dicts, one per CSV row
      - null_count: integer, count of rows with null actual_spend
      - null_details: list of dicts with keys {period, ward, category, notes} for each null row
    error_handling: |
      If file not found, raise FileNotFoundError with path shown.
      If required columns missing, raise ValueError listing missing columns.
      If CSV malformed, raise ValueError with line number and reason.
      Always return null_count and null_details even if 0 nulls present.

  - name: compute_growth
    description: Filters dataset to specific ward+category, computes period-over-period growth (MoM or YoY), returns per-period table with formula and null flags.
    input: |
      dataset (list of row dicts), ward (string, exact match), category (string, exact match), growth_type (string: "MoM" or "YoY")
    output: |
      list of dicts, each with keys: {period, actual_spend, previous_value, growth_percentage, formula, flag}
      - period: YYYY-MM format
      - actual_spend: float or null
      - previous_value: float (for formula reference) or null
      - growth_percentage: float (e.g., 33.1) or null
      - formula: string showing the computation (e.g., "(19.7 - 14.8) / 14.8 * 100")
      - flag: "NULL_ROW" if actual_spend is null, otherwise empty
    error_handling: |
      If growth_type not in ["MoM", "YoY"], raise ValueError: "growth_type must be 'MoM' or 'YoY'".
      If ward or category not found in dataset, return empty list with message.
      If null actual_spend encountered, set growth_percentage to null, set flag="NULL_ROW", set formula to "".
      Sort output by period ascending (YYYY-MM order).

skills:
  - name: load_dataset
    description: >
      Reads a budget CSV file, validates that required columns exist (period, ward,
      category, budgeted_amount, actual_spend, notes), counts null actual_spend rows
      and reports their locations and reasons before returning the data.
    input: File path (string) to a .csv budget file.
    output: List of dicts with all columns, plus a summary of null rows found.
    error_handling: >
      If the file does not exist, raise FileNotFoundError. If required columns are
      missing, raise ValueError listing which columns are absent. If the CSV is
      empty (no data rows), return an empty list and print a warning.

  - name: compute_growth
    description: >
      Takes a filtered list of rows (single ward + single category), the growth type
      (MoM or YoY), and returns a per-period table with growth_percent and
      formula_used columns. Null actual_spend rows are flagged, not computed.
    input: Filtered row list, growth_type string ("MoM" or "YoY").
    output: List of dicts with all original columns plus previous_period_actual,
      growth_percent, formula_used, null_flag, null_reason.
    error_handling: >
      If fewer than 2 periods are available, set growth_percent to 'N/A' and
      formula_used to 'Insufficient periods for growth computation'. For YoY with
      only one year of data, refuse with a message that YoY requires multi-year data.

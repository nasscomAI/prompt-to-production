skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that required columns exist,
      identifies null actual_spend rows, and returns the data with null
      information reported.
    input: >
      file_path (string): filesystem path to a CSV with columns: period
      (YYYY-MM), ward (string), category (string), budgeted_amount (float),
      actual_spend (float or blank), notes (string).
    output: >
      A tuple of (rows, null_report) where rows is a list of dicts with
      all columns parsed, and null_report is a list of dicts each with
      keys: period, ward, category, notes — one entry per null actual_spend
      row.
    error_handling: >
      If the file does not exist, raise FileNotFoundError. If required
      columns are missing, raise ValueError with the list of missing
      columns. If no rows are found, return ([], []) with a warning to
      stderr.

  - name: compute_growth
    description: >
      Takes filtered rows for a single ward and category, computes
      month-over-month growth on actual_spend, and returns a per-period
      table with formula shown. Null rows are flagged, not computed.
    input: >
      rows (list of dicts): filtered rows for one ward + category, each
      with keys: period, actual_spend (float or None), notes (string).
      growth_type (string): "MoM" for month-over-month.
    output: >
      A list of dicts, one per period, with keys: period, actual_spend,
      previous_month_spend, growth_absolute, growth_percent, formula_used,
      notes. Null rows have growth fields set to "N/A" and notes populated
      from the original data.
    error_handling: >
      If growth_type is not "MoM", raise ValueError. If the first month
      has no previous month, show growth fields as "N/A — first period".
      If a null row is encountered, flag it and continue to the next period.

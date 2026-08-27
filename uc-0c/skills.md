skills:
  - name: load_dataset
    description: >
      Reads a ward budget CSV, validates required columns, reports null
      count and which rows contain null actual_spend with their notes, and
      returns a clean DataFrame.
    input: >
      Path to CSV file (string). Expected columns: period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      A pandas DataFrame with parsed period (datetime), numeric columns
      coerced, and nulls preserved. The function also prints a null-rows
      report (count + per-row detail with notes) to stdout.
    error_handling: >
      Raises FileNotFoundError if path is invalid. Raises ValueError if
      any required column is missing or the file is empty.

  - name: compute_growth
    description: >
      Takes a ward, category, and growth-type filter, computes growth per
      period for that single ward/category pair, and returns a table with
      formula shown.
    input: >
      DataFrame (from load_dataset), ward (string), category (string),
      growth_type (string, one of \"MoM\" or \"YoY\").
    output: >
      A DataFrame with columns: ward, category, period, actual_spend,
      growth (float or blank), formula (string), null_flag (string or
      blank). For MoM, growth = (current - previous) / previous * 100
      within the same ward+category. For YoY, growth = (current - same
      month previous year) / same month previous year * 100. Rows with
      null actual_spend have blank growth and a null_flag set to the notes
      value.
    error_handling: >
      Raises ValueError if growth_type is not \"MoM\" or \"YoY\". Returns
      empty DataFrame if no data matches the given ward+category. For rows
      where the prior-period value is null or missing, growth is set to
      blank and formula indicates \"insufficient prior data\".

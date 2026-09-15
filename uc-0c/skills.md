# skills.md

skills:
  - name: load_dataset
    description: Read the ward-budget CSV, validate that all required columns exist, count nulls, and report which rows contain null actual_spend values before returning the data.
    input: File path (string) to a CSV with columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: Parsed DataFrame plus a null report listing each null row's period, ward, category, and notes reason.
    error_handling: If file is missing or required columns are absent, raise a clear error. If null count differs from expected, warn but continue.

  - name: compute_growth
    description: Given a specific ward, category, and growth type (MoM or YoY), compute period-over-period growth and return a per-period table with formula shown.
    input: ward (string), category (string), growth_type ("MoM" or "YoY"), filtered DataFrame.
    output: DataFrame with columns: period, actual_spend, previous_period, previous_spend, growth_pct, formula_used, null_flag, null_reason. Null rows appear with growth_pct = null and null_flag = true.
    error_handling: If ward or category not found in data, return an error listing valid options. If growth_type is not MoM or YoY, refuse and ask. If previous period is null, flag the row instead of computing.

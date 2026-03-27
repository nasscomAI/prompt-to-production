# skills.md

skills:
  - name: load_dataset
    description: Read a CSV budget file, validate columns, and report null count and affected rows before returning.
    input: Path to a CSV file with columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: Loaded data as a list of dicts, plus a null report listing which rows have null actual_spend and the reason from notes.
    error_handling: If required columns are missing or the file is empty, abort with an error. If nulls are found, report them — do not silently drop or impute.

  - name: compute_growth
    description: Take ward, category, and growth_type, compute per-period growth rates, return a table with the formula shown.
    input: Filtered data (ward, category), growth_type (MoM or YoY).
    output: Table of periods with actual_spend, growth_rate, and formula column. Null rows flagged with reason, not computed.
    error_handling: If growth_type is not specified, refuse and ask. If insufficient data points exist for the requested growth type, report it rather than returning partial results.

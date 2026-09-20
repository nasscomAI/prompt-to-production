# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: >
      Reads a ward budget CSV with utf-8-sig encoding and validates its expected
      columns (period, ward, category, budgeted_amount, actual_spend, notes).
    input: >
      Path to the budget CSV file (str).
    output: >
      Normalised rows plus the distinct ward and category lists; blank numeric
      fields are converted to None and collected into a null report.
    error_handling: >
      A missing file, missing columns, or an empty dataset is rejected with a
      descriptive error before any computation starts.

  - name: compute_growth
    description: >
      Computes per-period growth for a single ward x category series using the
      requested growth type.
    input: >
      Filtered and period-sorted rows for one ward and one category, plus the
      growth type ("MoM" or "YoY").
    output: >
      One result row per period with growth_pct, growth_type, a formula string,
      and a null_flag marking rows whose source data is blank.
    error_handling: >
      The first period of a MoM series has no prior period and yields NULL growth
      with a no-prior-period reason; blank actual_spend yields NULL growth with
      null_flag=YES. NaN or infinite results are rendered as NULL, never rounded
      into a misleading number.
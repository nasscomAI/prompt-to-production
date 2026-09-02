# skills.md — UC-0C Budget Growth

skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate its columns, and report null actual_spend rows before returning the data.
    input: >
      input_path (str) to ward_budget.csv with columns: period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      Structured rows preserving each field, plus a null report listing the count
      and the exact (period, ward, category) of every row whose actual_spend is
      blank, together with that row's notes reason. Blank actual_spend is kept as
      a null marker, never converted to 0.
    error_handling: >
      If the file is missing or a required column is absent, raise a clear error
      before any computation. A blank actual_spend is preserved as null (not
      coerced to zero or skipped). Rows are returned in period order so
      consecutive-month growth can be computed reliably.

  - name: compute_growth
    description: Compute per-period growth for a single ward + category, showing the formula per row and flagging nulls, or refuse.
    input: >
      ward (str), category (str), growth_type (str: MoM or YoY), and the dataset
      from load_dataset.
    output: >
      A per-period table (one row per month for that ward + category) with fields:
      period, ward, category, actual_spend, growth_type, growth_pct (or
      NOT_COMPUTED), formula, and flag/reason. MoM% = (actual[m] - actual[m-1]) /
      actual[m-1] * 100, rounded to 1 decimal place, shown with real numbers in
      the formula field.
    error_handling: >
      Refuses (returns no numbers) if ward or category is missing, empty, or
      'all'/wildcard, or if growth_type is not supplied. Marks NOT_COMPUTED with a
      reason for: the first month (no prior period), any null actual_spend row
      (reason from notes), and any month immediately after a null. YoY is reported
      NOT_COMPUTED ('no prior-year data') because the dataset is 2024 only. Never
      aggregates across wards, categories, or periods and never imputes a null.

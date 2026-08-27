skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates required columns exist, counts
      null `actual_spend` rows, and reports each null row's details (period,
      ward, category, notes) before returning the DataFrame.
    input: >
      File path string (e.g. `--input ../data/budget/ward_budget.csv`).
    output: >
      A pandas DataFrame with columns: period, ward, category, budgeted_amount,
      actual_spend, notes.
    error_handling: >
      Raises FileNotFoundError if the path does not exist. Raises ValueError
      if any required column is missing from the CSV. If every row has null
      `actual_spend`, warns and returns the DataFrame anyway — growth cannot
      be computed.

  - name: compute_growth
    description: >
      Takes a ward, category, and growth type, filters the dataset to that
      ward+category, sorts by period, and computes the per-period growth
      rate. Returns a table with growth values and the formula used.
    input: >
      DataFrame (from load_dataset), ward string, category string,
      growth_type string ("MoM" or "YoY").
    output: >
      A DataFrame with columns: period, ward, category, actual_spend,
      previous_spend, growth_pct, formula, null_flag.
    error_handling: >
      Raises ValueError if growth_type is not "MoM" or "YoY". Raises
      ValueError if the ward+category combination yields zero rows. If the
      prior-comparison period is missing (no previous month for MoM, or 12
      months before for YoY), sets growth_pct to NULL and null_flag to
      "insufficient data — no prior period". If a row's actual_spend is
      NULL, sets growth_pct to NULL and null_flag to the value from the
      notes column.

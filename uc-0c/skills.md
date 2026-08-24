# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates the required columns, and reports the
      null actual_spend rows with their notes BEFORE any computation happens.
    input: >
      Path to ../data/budget/ward_budget.csv — 300 rows, columns period, ward,
      category, budgeted_amount, actual_spend, notes.
    output: >
      Returns the parsed rows plus a null report listing every row where
      actual_spend is blank (period, ward, category, notes reason).
    error_handling: >
      Raises an error if required columns are missing. Null rows are flagged and
      their reason is reported — they are never filled in or silently skipped.

  - name: compute_growth
    description: >
      Computes a growth table for exactly one ward + one category at the requested
      growth type (MoM or YoY), showing the formula used in every output row.
    input: >
      The parsed dataset, a single ward, a single category, and the growth type
      (MoM | YoY).
    output: >
      Writes uc-0c/growth_output.csv with per-period rows for the requested ward
      and category: period, actual_spend, previous period value, growth %, formula,
      and status. Null rows are written as FLAGGED_NULL with their reason and are
      never computed.
    error_handling: >
      Refuses to aggregate across wards or categories. Refuses to guess a growth
      type — if it is not specified, computation is refused. If the previous period
      value is missing or zero, the row is flagged rather than guessed.

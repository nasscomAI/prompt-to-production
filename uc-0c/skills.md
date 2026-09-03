# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Load ward_budget.csv, validate its schema, and report every null actual_spend row up front.
    input: >
      A filesystem path (string) to the ward_budget CSV passed via
      --input. Expected columns: period, ward, category, budgeted_amount,
      actual_spend, notes.
    output: >
      A tuple (rows, null_report) where rows is the list of dicts and
      null_report is a list of dicts describing each null actual_spend
      row: {period, ward, category, notes}. null_report is empty only
      if the dataset has zero nulls.
    error_handling: >
      Refuse (non-zero exit) if the file is missing, unreadable, has
      the wrong columns, or has zero rows. The null_report is a
      required output — it is never optional. Every null row must be
      surfaced before compute_growth is called.

  - name: compute_growth
    description: Compute period-over-period growth for a single (ward, category) series using the requested growth_type.
    input: >
      (rows, ward, category, growth_type, null_report).
      growth_type must be one of "MoM", "QoQ", "YoY".
    output: >
      A list of dicts written to --output as CSV. Columns:
      period, ward, category, actual_spend, prior_period, prior_spend,
      growth_value, growth_type, formula, note. Rows whose prior period
      is null or whose current period is null have growth_value=NULL
      and note="null flagged; growth not computed". A header section
      also lists every null flagged in the series.
    error_handling: >
      If (ward, category) is not found, refuse. If multiple series
      match, refuse. If growth_type is missing or not in
      {MoM, QoQ, YoY}, refuse and ask. Never compute growth across
      two different wards or two different categories — the agent
      must not aggregate, average, sum, or roll up the series. If the
      prior period's actual_spend is zero, refuse to divide (division
      by zero) and flag the row.

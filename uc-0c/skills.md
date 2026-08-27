# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: >
      Reads the ward_budget CSV, validates required columns, reports the
      count and details of null actual_spend rows before returning.
    input: >
      input_path (str — path to ward_budget.csv with columns: period, ward,
      category, budgeted_amount, actual_spend, notes)
    output: >
      tuple of (list[dict] — all rows, list[dict] — rows where actual_spend
      is null/missing with their notes)
    error_handling: >
      If the file is missing or required columns are absent, raise
      FileNotFoundError or ValueError with a descriptive message. Always
      report null rows before returning data.

  - name: compute_growth
    description: >
      Takes filtered rows for a single ward+category, sorts by period, and
      computes MoM or YoY growth. Returns a table with period, actual_spend,
      previous_actual, growth_rate, formula, and flag for each period.
    input: >
      rows (list[dict] — sorted by period), growth_type (str — "MoM" or
      "YoY"), ward (str), category (str)
    output: >
      list[dict] with keys: period, ward, category, actual_spend,
      prev_period_actual, growth_rate, formula, flag
    error_handling: >
      If actual_spend is null, set growth_rate="N/A", formula="Not computed —
      null actual_spend", flag=reason from notes. If no previous period exists
      for growth calculation, set growth_rate="N/A", formula="No previous
      period for comparison", flag="N/A - first period".

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates expected columns are present, and reports the null count and which specific rows are null before returning any data.
    input:
      type: file path + filter parameters
      format: "CSV file path, plus ward (str) and category (str) filter values"
    output:
      type: list of row objects + null report
      format: "{rows: [{period, ward, category, budgeted_amount, actual_spend: float or None, notes}, ...] filtered to the requested ward/category, null_report: [{period, ward, category, reason}] for any null actual_spend rows in that slice}"
    error_handling: >
      If the file does not exist, raise a clear error and stop. If required
      columns (period, ward, category, budgeted_amount, actual_spend, notes)
      are missing, raise an error naming which columns are absent. If the
      requested ward/category combination produces zero matching rows,
      raise an error naming the requested ward and category rather than
      returning an empty dataset silently.

  - name: compute_growth
    description: Computes growth (of the type specified by --growth-type) for the filtered ward/category series, showing the formula used and flagging any period that cannot be computed due to a null value.
    input:
      type: list of row objects + growth type
      format: "rows as produced by load_dataset, plus growth_type (str) — required, never defaulted"
    output:
      type: CSV rows
      format: "period, ward, category, actual_spend, prior_period_spend, growth_pct, formula_used, flag — written to growth_output.csv"
    error_handling: >
      If growth_type is not provided, raise an error asking the caller to
      specify one — never silently default to MoM. If a row's actual_spend
      or the prior period's actual_spend is null, do not compute growth_pct
      for that row — leave it blank, set flag to the null reason from the
      notes column (e.g. 'null: data not yet reconciled'), and still show
      the formula that would have been used had the data been present.

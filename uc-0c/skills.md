skills:
  - name: load_dataset
    description: Reads and validates the ward budget CSV before analysis.
    input: A filesystem path to a CSV with period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: Validated rows plus a report of null actual_spend count, periods, wards, categories, and notes.
    error_handling: Rejects missing columns, malformed numeric values, empty files, and all-ward or all-category requests; reports every null row instead of skipping it.
  - name: compute_growth
    description: Computes a per-period growth table for one ward and category using the explicitly selected formula.
    input: Validated rows, one ward, one category, and growth_type such as MoM.
    output: CSV rows containing period, ward, category, actual_spend, growth_type, formula, growth_percent, and status.
    error_handling: Refuses missing or unsupported growth types; marks null actual spend and periods without a prior value as NOT_COMPUTED with an explanation.

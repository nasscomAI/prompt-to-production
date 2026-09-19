# UC-0C skills

skills:
  - name: load_dataset
    description: Read and validate the budget CSV while reporting all null actual_spend rows.
    input: CSV path.
    output: Validated rows and a null report containing period, ward, category, and notes.
    error_handling: Reject missing columns or a missing dataset; preserve nulls rather than imputing them.

  - name: compute_growth
    description: Compute per-period growth for one ward/category series with explicit formulas.
    input: Rows, one ward, one category, and an explicit growth type.
    output: Per-period table with actual spend, growth percentage, formula, status, and notes.
    error_handling: Refuse all-ward/all-category requests and flag rows whose current or prior actual spend is null.

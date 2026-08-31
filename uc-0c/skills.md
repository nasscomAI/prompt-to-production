# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, reports null actual_spend rows and their reasons, and returns the dataset.
    input: A path to a CSV file containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: A validated list of budget records together with null-row information.
    error_handling: Reject missing files, missing required columns, malformed data, and report null actual_spend values without replacing them.

  - name: compute_growth
    description: Computes the requested growth type for one ward and one category and includes the calculation formula with every result.
    input: A validated dataset, one ward, one category, and an explicitly specified growth type.
    output: A per-period table containing actual spend, formula, growth result, and null flags where applicable.
    error_handling: Refuse unspecified growth types and cross-ward or cross-category aggregation; flag null actual_spend rows instead of calculating them.

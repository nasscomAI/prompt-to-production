# skills.md

skills:
  - name: load_dataset
    description: >
      Loads the budget CSV, validates required columns, and reports
      missing actual_spend values with their row details and notes.
    input: >
      CSV file path containing period, ward, category, budgeted_amount,
      actual_spend, and notes columns.
    output: >
      Validated structured dataset with null rows identified.
    error_handling: >
      Reject the dataset if required columns are missing or the input
      cannot be read.

  - name: compute_growth
    description: >
      Computes the requested growth type for one ward and one category
      while preserving null handling and showing the formula.
    input: >
      Structured dataset, one ward, one category, and an explicit
      growth type such as MoM.
    output: >
      Per-period table containing period, actual_spend, growth formula,
      growth result, and null flags where applicable.
    error_handling: >
      Refuse when ward or category is missing, when the growth type is
      not explicitly provided or unsupported, or when an actual_spend
      value required for calculation is null.
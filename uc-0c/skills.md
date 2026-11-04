skills:
- name: load_dataset
  description: Loads and validates the municipal budget dataset.
  input: >
  CSV file containing period, ward, category, budgeted_amount,
  actual_spend and notes columns.
  output: >
  Validation report including row count, null count and list
  of rows containing null actual_spend values.
  error_handling: >
  Reject files with missing required columns and report null rows
  before analysis.

- name: compute_growth
  description: Calculates growth metrics for a specified ward and category.
  input: >
  Validated dataset, ward name, category name and growth type.
  output: >
  Per-period growth table including formula, growth percentage,
  and any null flags.
  error_handling: >
  Refuse computation if growth type is missing. Do not calculate
  growth where actual_spend is null.

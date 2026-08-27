# skills.md

skills:

- name: load_dataset
  description: >
  Loads the CSV dataset and validates structure, while identifying null values.
  input: >
  File path to CSV dataset
  output: >
  Parsed dataset along with:
  - list of null rows (period, ward, category)
  - count of nulls
    error_handling: >
    If required columns are missing, raise error.
    If file unreadable, terminate execution with message.

- name: compute_growth
  description: >
  Computes growth (MoM or YoY) for a specific ward and category,
  returning per-period values with formulas and null flags.
  input: >
  dataset, ward (string), category (string), growth_type (MoM or YoY)
  output: >
  Table with:
  - period
  - actual_spend
  - growth
  - formula
  - flag (if null)
    error_handling: >
    If null values exist for a period or previous period, skip computation
    and flag the row. If growth_type is missing, refuse execution.

- name: load_dataset
  description: Reads CSV file, validates required columns, and reports null rows.
  input:
    type: CSV file
    format: ward budget dataset with period, ward, category, actual_spend
  output:
    type: list
    format: validated dataset rows
  error_handling: >
    If required columns are missing, raise error.
    If null values exist, identify and report them with period, ward, category, and notes.

- name: compute_growth
  description: Computes growth per period for a specific ward and category.
  input:
    type: parameters
    format: ward, category, growth_type (MoM)
  output:
    type: CSV rows
    format: period, actual_spend, growth, formula
  error_handling: >
    If growth_type is missing, refuse.
    If actual_spend is null, flag and skip computation.
    If filtering results in no data, return error.
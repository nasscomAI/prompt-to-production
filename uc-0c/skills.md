- name: load_dataset
  description: Reads the ward budget CSV, validates the required columns, reports the total null count and identifies every null actual_spend row before returning the dataset.
  input:
    type: CSV file
    format: "CSV containing period, ward, category, budgeted_amount, actual_spend, and notes columns"
  output:
    type: validated dataset with null report
    format: "Validated tabular data plus null count and each null row with its period, ward, category, and notes reason"
  error_handling: >
    Reject the input if required columns are missing or the CSV cannot be read.
    Treat blank actual_spend values as null. Report every null row and its
    notes reason before returning the dataset. Do not silently drop null rows.

- name: compute_growth
  description: Computes the requested growth type for the explicitly selected ward and category and returns a per-period table with the formula shown.
  input:
    type: ward, category, and growth type
    format: "ward string, category string, and explicitly specified growth type such as MoM"
  output:
    type: per-period growth table
    format: "CSV/table rows containing period, ward, category, actual values, formula used, growth result, and any null flag or reason"
  error_handling: >
    Refuse when growth_type is missing or ambiguous rather than guessing.
    Refuse requests that aggregate across wards or categories unless explicitly
    instructed. Flag rows affected by null actual_spend values and report the
    corresponding notes reason. Do not compute a growth result when a required
    value is null.

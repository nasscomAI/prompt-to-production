# skills.md

skills:

- name: load_dataset
  description: Load the budget CSV, validate required columns, and report null actual_spend rows before any calculations.
  input: A file path to the budget CSV.
  output: A structured list of rows with validation details, including the count and reasons for null actual_spend values.
  error_handling: If required columns are missing or the CSV is unreadable, return a clear validation error and do not proceed.

- name: compute_growth
  description: Compute growth for one specified ward and category using the requested growth type and return a per-period table with formula metadata.
  input: A filtered dataset plus ward, category, and growth-type parameters.
  output: A table of period-by-period results with actual spend, growth percentage, formula used, and null-flagged rows where applicable.
  error_handling: If the growth type is missing, the scope is broader than a single ward and category, or the input is invalid, return a refusal or validation error instead of guessing.

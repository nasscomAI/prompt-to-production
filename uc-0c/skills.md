skills:

- name: load_dataset
  description: Reads the ward budget CSV, validates required columns, and reports null actual_spend rows with their notes.
  input: A string file path to the input CSV file.
  output: A validated dataset object or list containing rows with fields: period, ward, category, budgeted_amount, actual_spend, notes, and null metadata.
  error_handling: If the file is missing, unreadable, or missing required columns, abort with a descriptive error. If data rows contain unexpected schema, raise a validation error.

- name: compute_growth
  description: Computes per-period growth for a specified ward and category using the requested growth type and attaches the exact formula used.
  input: A validated dataset object, a ward string, a category string, and a growth_type string (`MoM` or `YoY`).
  output: A per-period list of rows containing period, ward, category, actual_spend, growth, formula, notes, and null flags.
  error_handling: If growth_type is missing or unsupported, or if ward/category do not match dataset values, refuse with a clear error. If actual_spend is NULL, do not compute growth for that row and preserve the notes.

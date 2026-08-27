# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates the required columns, and reports null counts and the affected rows before returning the dataset.
    input: A file path to the CSV and an optional expected schema.
    output: A structured dataset object with the rows, column validation result, null row inventory, and any schema errors.
    error_handling: If the file is missing or required columns are absent, return a clear validation error and stop rather than proceeding.

  - name: compute_growth
    description: Computes growth for a single ward and single category using the requested growth type and returns a per-period table with the formula shown for each row.
    input: A validated dataset, a ward name, a category name, and a growth type such as MoM or YoY.
    output: A table of growth results with columns for period, actual spend, growth value, formula, and null/flag status.
    error_handling: If the input is ambiguous, missing, or would require aggregation across multiple wards or categories, return a refusal message and do not compute.

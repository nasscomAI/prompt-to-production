# skills.md

skills:

* name: load_dataset
  description: Read the supplied ward budget CSV, validate its required columns, identify null actual_spend values, and return the validated dataset.
  input: CSV file path containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
  output: Validated dataset with the total null count and the rows containing null actual_spend values, including their notes reasons.
  error_handling: If the file is missing, unreadable, empty, malformed, or missing required columns, report the error and do not continue with incomplete data.

* name: compute_growth
  description: Calculate period-by-period growth for the explicitly requested ward and category using the explicitly selected growth type.
  input: Validated dataset plus a ward name, category name, and growth type such as MoM or YoY.
  output: Per-period table containing the period, ward, category, actual spend, formula used, growth result, and calculation status.
  error_handling: If the ward, category, or growth type is missing or invalid, refuse to calculate. If actual_spend or another required comparison value is null, flag the row, report the null reason from notes, and do not compute the growth value.

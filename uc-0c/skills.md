- name: load_dataset
  description: Reads the budget CSV file, validates the presence of required columns (period, ward, category, budgeted_amount, actual_spend, notes), and reports the count and details of null actual_spend rows.
  input: CSV file path (string)
  output: Validated dataset (structured object/dataframe) and a summary of null rows.
  error_handling: Throws an error if the file is missing or columns are incorrect; if nulls are found in actual_spend, it explicitly flags them and retrieves the null reason from the notes column.

- name: compute_growth
  description: Calculates the specified growth metric (MoM or YoY) for a specific ward and category, returning a per-period table that includes the formula used for each calculation.
  input: ward (string), category (string), growth_type (string: MoM/YoY), dataset (structured object)
  output: Per-period growth table (CSV format/structured object) with growth values and formula strings.
  error_handling: Refuses to guess if growth_type is missing; if ward or category are invalid or missing, it refuses to aggregate data; if a null row is encountered, it flags the row as "NULL" and does not compute the growth for that period.

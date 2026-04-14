- name: load_dataset
  description: Reads the budget CSV file, validates the presence of required columns, and reports the count and details of null actual_spend rows.
  input: path (string, absolute or relative file path to ward_budget.csv)
  output: data (table structure) and null_audit (dictionary listing null-row periods and their associated notes)
  error_handling: Fails if columns are missing or file is corrupted; must explicitly register and report the 5 deliberate null rows and their rejection reasons from the notes column.

- name: compute_growth
  description: Computes period-over-period growth for a specific ward and category while documenting the specific formula used for each row.
  input: ward (string), category (string), growth_type (string: 'MoM' or 'YoY')
  output: growth_table (list of dictionaries containing period, growth percentage, and formula string)
  error_handling: Refuses execution if growth_type is missing or if aggregation across multiple wards/categories is requested; flags null rows as "not computed" and reports notes rather than returning silent results.

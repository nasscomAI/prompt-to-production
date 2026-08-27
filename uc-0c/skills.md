# skills.md

skills:

- name: load_dataset
  description: Loads and validates the ward budget CSV dataset, reporting null counts and which rows have nulls.
  input: File path to ward_budget.csv.
  output: A list of dictionaries representing the CSV rows, with validation report on nulls.
  error_handling: If file not found or columns missing, return error message with details.

- name: compute_growth
  description: Computes month-over-month growth rates for a specific ward and category, flagging nulls and showing formulas.
  input: Dataset list, ward name, category name, growth type (must be 'MoM').
  output: List of dictionaries with ward, category, period, actual_spend, growth_rate, formula, notes.
  error_handling: If ward/category not found, return empty list; if growth_type not 'MoM', refuse; flag null rows appropriately.

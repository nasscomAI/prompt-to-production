- name: load_dataset
  description: Loads CSV dataset
  input: CSV file path
  output: dataset rows
  error_handling: return error if file missing or invalid

- name: compute_growth
  description: Calculates month-over-month growth
  input: dataset, ward, category
  output: growth value
  error_handling: return error if missing or invalid data
  
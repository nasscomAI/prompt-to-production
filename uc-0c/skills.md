skills:

- name: calculate_growth
  description: Calculates spending growth for each ward and category using the budget dataset.
  input: CSV row containing ward name, category, and spending values for different periods.
  output: Calculated growth value for that ward and category.
  error_handling: If required values are missing or invalid, mark the row for review instead of calculating incorrect growth.

- name: generate_growth_report
  description: Reads the full budget CSV dataset and produces a report of spending growth per ward and per category.
  input: Budget CSV file (ward_budget.csv).
  output: Output CSV file containing ward, category, and growth values.
  error_handling: Skip empty rows and flag rows with incomplete data so the program does not crash.

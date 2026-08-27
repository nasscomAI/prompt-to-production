- name: load_dataset
  description: Reads the budget CSV file, validates the required columns, and explicitly reports the count and location of null values before returning the data.
  input: string (file path to the dataset, e.g., '../data/budget/ward_budget.csv')
  output: object (parsed dataset and a report detailing null row locations and reasons)
  error_handling: If the file is missing or columns are incorrect, return an error. If actual_spend contains nulls, do not silently handle them; explicitly flag every null row and report the reason from the notes column before returning.

- name: compute_growth
  description: Computes period-over-period growth for a specific ward and category, returning a per-period table that shows the exact formula used for each row.
  input: object (ward as string, category as string, growth_type as string)
  output: object (per-ward, per-category table of results with growth metrics and the formula string)
  error_handling: If growth_type is missing, refuse to compute and ask the user rather than assuming a formula. If asked to aggregate across multiple wards or categories, refuse and throw an error indicating wrong aggregation level.
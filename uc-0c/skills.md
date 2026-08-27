skills:

- name: load_dataset
  description: Reads the budget CSV dataset, validates the standard columns, and scans for explicit nulls in actual_spend beforehand.
  input: File path string pointing to the CSV dataset.
  output: A dictionary containing the parsed valid records, and a list of identified null rows with their period, ward, category, and explanatory notes.
  error_handling: System exits if the file path is broken; explicitly catches non-float null strings instead of silently throwing type errors.

- name: compute_growth
  description: Computes period-over-period growth for a specific isolated ward and category combo, surfacing exactly the formula used.
  input: Valid records, ward string, category string, and growth_type.
  output: A list of dictionaries representing the per-period table including `period`, `actual_spend`, `growth`, and `formula`.
  error_handling: Return a strict refusal note if ward/category filters are missing, or if growth-type is unspecified/invalid. Emits an uncalculated flagged row for periods containing null data.

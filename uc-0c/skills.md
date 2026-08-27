skills:

- name: load_dataset
  description: Loads and validates the dataset, identifying null values and affected rows.
  input: Path to CSV file.
  output: List of rows with validation summary (including null rows).
  error_handling:
  If file is missing or malformed, return empty dataset and error message.

- name: compute_growth
  description: Computes growth for a given ward and category with explicit formula.
  input: Dataset, ward name, category name, growth type (MoM).
  output: Table of period-wise growth values with formula included.
  error_handling:
  If null values exist, flag them and skip computation for those rows.
  If growth-type is missing, refuse computation.

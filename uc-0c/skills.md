skills:
  - name: load_dataset
    description: Loads and validates the budget dataset, identifying null values.
    input: File path to CSV dataset.
    output: List of dataset rows and report of null rows.
    error_handling: If file is missing or corrupted, return empty dataset and log error.

  - name: compute_growth
    description: Computes growth metrics per ward and category using specified growth type.
    input: Dataset rows, ward, category, growth_type.
    output: List of rows with computed growth values and formulas.
    error_handling: If required values are missing, skip row and flag it with reason.
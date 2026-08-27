skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the expected columns, and identifies rows with null spend values before returning the data.
    input: File path to the budget CSV (string).
    output: A list of dicts containing the dataset rows.
    error_handling: Raises an error if required columns are missing.

  - name: compute_growth
    description: Computes Month-on-Month (MoM) or Year-on-Year (YoY) spend growth for a specific ward and category.
    input: A dictionary of filtered data, and the selected growth type (MoM or YoY).
    output: A list of dicts containing period, actual spend, growth percentage, the formula used, and notes/status.
    error_handling: Refuses calculation if growth type is not specified or if an all-ward/all-category aggregate is requested.

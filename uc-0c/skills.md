skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the required columns (period, ward, category, actual_spend), and identifies any rows with missing spending data.
    input: Path to the budget CSV file.
    output: A list of validated row objects and a separate report of rows with NULL values.
    error_handling: Raises an error if mandatory columns are missing or if the file cannot be accessed.

  - name: compute_growth
    description: Calculates Month-over-Month (MoM) or Year-over-Year (YoY) growth for a specific ward and category, including the formula in each result row.
    input: Ward name, category name, growth type (MoM or YoY), and the dataset.
    output: A structured table (list of dicts) with period, actual_spend, growth_value, and formula.
    error_handling: Refuses to compute if the growth type is missing or if asked to aggregate across multiple wards/categories.

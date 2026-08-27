skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and identifies rows with null actual_spend values.
    input: File path (string) to the CSV dataset.
    output: A dictionary containing the DataFrame and a list of identified null rows with their notes.
    error_handling: Refuses if required columns (period, ward, category, budgeted_amount, actual_spend) are missing.

  - name: compute_growth
    description: Calculates growth (MoM) for a specific ward and category, flagging nulls and including calculation formulas.
    input: A dictionary containing ward (string), category (string), growth_type (string), and the dataset (DataFrame).
    output: A list of dictionaries representing the growth table with columns for period, actual_spend, growth, and formula.
    error_handling: Refuses if growth_type is not specified or if asked to aggregate across wards/categories.

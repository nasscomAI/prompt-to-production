skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports the count and locations of any null actual_spend rows.
    input: File path to the CSV dataset (string).
    output: A list of dictionaries representing the rows of the dataset.
    error_handling: If the file is missing or columns are malformed, raise an error. If there are null actual_spend values, report the count and reasons to standard output before returning the dataset.

  - name: compute_growth
    description: Calculates the specified growth type (e.g., MoM) for a specific ward and category over time.
    input: The dataset (list of dicts), target ward (string), target category (string), and growth_type (string).
    output: A list of dictionaries representing the result table with period, ward, category, actual_spend, growth, formula, and notes.
    error_handling: If ward or category is 'Any' or missing, raise a Refusal error. If growth_type is missing, raise a Refusal error.

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the headers, and scans for and logs any rows with null actual_spend values.
    input: Path to the input budget CSV file (string).
    output: A list of dicts representing the dataset rows.
    error_handling: Raises an exception if required columns are missing or if the file cannot be read, and outputs a list of identified null rows.

  - name: compute_growth
    description: Computes period-over-period spend growth for a specific ward and category using the specified growth type.
    input: Dataset rows (list of dicts), target ward name (string), target category (string), and growth type (string, e.g., 'MoM').
    output: A list of dicts with keys period, actual_spend, growth, and formula, including flags/notes for null rows.
    error_handling: Refuses calculation if growth type is not provided, if asked to aggregate across all wards/categories, or flags null actual_spend rows as 'NULL' with the reason from the notes column.

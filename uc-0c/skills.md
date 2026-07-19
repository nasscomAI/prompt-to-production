skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, validates the columns, and checks for and logs any null actual_spend rows.
    input: Absolute path to the budget CSV file (string).
    output: A list of dictionaries representing the rows in the CSV.
    error_handling: Raises a FileNotFoundError if the file doesn't exist, or a ValueError if headers are incorrect. Logs the count and line numbers of any null values detected.

  - name: compute_growth
    description: Filters the dataset to the specified ward and category, sorts by period, and calculates period-over-period growth with formulas.
    input: A dictionary containing the keys: dataset (list of dicts), ward (string), category (string), growth_type (string).
    output: A list of dicts containing the computed growth rates, formula strings, and notes for each period.
    error_handling: Refuses execution and raises an error if ward or category represents an aggregate, if they are empty, or if growth_type is not provided.

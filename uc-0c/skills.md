skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates that all required columns are present, and checks for any null actual_spend rows.
    input: A string representing the file path of the CSV budget dataset.
    output: A list of dictionaries representing the rows of the dataset, and a report of any detected null actual_spend rows.
    error_handling: If the file is missing or required columns are absent, raises an appropriate FileNotFoundError or ValueError.

  - name: compute_growth
    description: Computes period-by-period spend growth for a specific ward and category using the specified growth type.
    input: A dictionary containing the keys 'dataset' (list of rows), 'ward' (string), 'category' (string), and 'growth_type' (string).
    output: A list of dictionaries representing the per-period growth table, with actual spend, growth percentage, mathematical formula, and notes.
    error_handling: Refuses to compute if ward, category, or growth_type is missing, or if asked to aggregate. Flags current or prior null values as NULL growth.

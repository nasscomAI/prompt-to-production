skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, reports the null actual_spend count and their row details.
    input: input_path (str) to the ward budget CSV file.
    output: A list of dictionaries representing the raw rows of the dataset.
    error_handling: Raises FileNotFoundError if the file is missing; raises ValueError if required columns are missing.

  - name: compute_growth
    description: Filters data by ward and category, calculates growth according to the selected growth_type, formats the formula, and handles null rows.
    input: dataset (list of dicts), ward (str), category (str), growth_type (str).
    output: A list of dictionaries representing the growth calculation rows.
    error_handling: Refuses if ward/category arguments ask for all-ward/all-category aggregation, or if growth_type is not specified.

skills:
  - name: load_dataset
    description: Reads the CSV dataset from the specified path, validates the required schema columns, identifies and reports the count and locations of null actual spend values, and returns the dataset.
    input: input_path (string, path to the CSV dataset file)
    output: A validated dataset object (e.g., pandas DataFrame) containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    error_handling: Raises a FileNotFoundError if the path is invalid, or a ValueError if required columns are missing or schema validation fails.

  - name: compute_growth
    description: Computes localized period-over-period growth metrics for a specific ward and category combination, generating the growth percentage and formula used while flagging null spend rows with their notes.
    input: dataset (DataFrame), ward (string), category (string), growth_type (string, e.g., 'MoM')
    output: A per-period table (DataFrame) containing calculated growth percentages, the exact mathematical formulas used for computation, and flagged null rows with their notes/reasons.
    error_handling: Raises a ValueError and refuses to proceed if growth_type is not specified or is unsupported. Raises a ValueError and refuses to proceed if asked to aggregate across multiple wards or categories. Raises a KeyError if the requested ward or category is not found in the dataset.

# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the CSV, validates columns, counts the total null actual_spend rows globally, and logs them before returning the dataset.
    input: >
      file_path (str): Path to the input CSV file.
    output: >
      A list of dictionaries representing the rows of the CSV.
    error_handling: >
      If the file cannot be found or read, raise FileNotFoundError.
      Must print a warning explicitly reporting any rows with null actual_spend.

  - name: compute_growth
    description: Takes the dataset and computes safe MoM or YoY growth for a exactly specified ward and category.
    input: >
      data (list of dict): The raw dataset.
      ward (str): The specific ward to filter for.
      category (str): The specific category to filter for.
      growth_type (str): "MoM" or "YoY" (must be explicit).
    output: >
      A list of dictionaries representing the growth output.
      Keys: period, ward, category, actual_spend, growth_pct, formula, flag
    enforcement:
      - "Refuse execution if multiple wards/categories are present but not specified."
      - "Refuse execution if growth_type is missing or invalid."
      - "Skip growth calculation if actual_spend is null or prior period is null, and instead flag it."
      - "Append the exact mathematical formula string to the output dictionary."
    error_handling: >
      Raise ValueError if filters do not uniquely resolve unless aggregations was explicitly bypassed.
      Raise ValueError if growth_type is invalid.

skills:
  - name: load_dataset
    description: Load the CSV dataset, check structure, count null values, and print details of null rows before processing.
    input: File path of the budget CSV file.
    output: List of dictionaries representing valid data rows.
    error_handling: Raise ValueError if required columns are missing.

  - name: compute_growth
    description: Filter data by ward and category, compute MoM growth chronologically, output the formula alongside the results, and flag null-related issues.
    input: Filter parameters (ward, category, growth_type) and the dataset list.
    output: List of dictionaries with calculated growth metrics and formulas.
    error_handling: Refuse calculation if parameters are missing or set to aggregate multiple categories or wards.

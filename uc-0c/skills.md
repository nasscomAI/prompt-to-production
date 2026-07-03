skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the columns, and checks/reports details of any null actual_spend rows.
    input: Path to the input CSV file.
    output: A list of dictionaries representing the rows in the CSV.
    error_handling: Raises ValueError if the file does not contain all required columns, or FileNotFoundError if the file is missing.

  - name: compute_growth
    description: Filters budget rows by ward and category, and calculates MoM or YoY growth per period, including the formula used and flagging null rows.
    input: A tuple or dictionary containing ward, category, growth_type, and the loaded dataset list.
    output: A list of dicts with calculated growth, formula, actual_spend, and notes for nulls.
    error_handling: Raises ValueError if growth_type is not provided, or if the ward/category combination matches nothing.

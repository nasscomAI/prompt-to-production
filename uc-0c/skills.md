skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates expected headers, detects any null actual_spend rows, and reports the null count and reasons.
    input: Path to the budget CSV file (.csv).
    output: A list of dictionaries representing the budget rows.
    error_handling: Raises an exception if required columns are missing or if the file cannot be read.

  - name: compute_growth
    description: Calculates growth (e.g., MoM) for a specific ward and category over time, flagging nulls and showing the mathematical formula used.
    input: A tuple/parameters containing the loaded dataset, ward name, category name, and growth type.
    output: A list of dictionaries containing period, actual_spend, growth_value, formula, and notes.
    error_handling: Refuses calculation and exits if ward/category filters are missing or if growth type is not specified.

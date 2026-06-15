skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the expected columns, and prints the count of null values before returning the records.
    input:
      type: str
      format: Path to the budget CSV file.
    output:
      type: list
      format: A list of dictionaries representing the rows in the CSV.
    error_handling: Raises FileNotFoundError if the path is invalid, or ValueError if the required columns are missing.

  - name: compute_growth
    description: Computes the growth rates for a filtered ward and category, flagging any null values with notes and outputting the mathematical formulas used.
    input:
      type: dict
      format: A dictionary containing 'data' (list of rows), 'ward' (str), 'category' (str), and 'growth_type' (str).
    output:
      type: list
      format: A list of dictionaries representing the periods and growth calculation details.
    error_handling: Refuses calculation and raises ValueError if ward, category, or growth_type are empty or invalid.

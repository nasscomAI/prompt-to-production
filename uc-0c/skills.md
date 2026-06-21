skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the expected schema columns, and logs any missing fields or empty actual spend values.
    input: The path to the CSV file (`input_path`).
    output: A list of dicts representing raw records.
    error_handling: Exits with an error if columns are missing or if the file cannot be accessed.

  - name: compute_growth
    description: Validates arguments to prevent aggregation, filters records, sorts chronologically, computes MoM/YoY growth, flags null inputs, and writes the growth table with calculation formulas.
    input: The dataset list, ward, category, growth_type, and output_path.
    output: Writes the result to the target CSV file.
    error_handling: Refuses execution and exits if ward/category is 'All' or empty, or if growth_type is missing.

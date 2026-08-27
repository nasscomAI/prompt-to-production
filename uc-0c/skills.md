# skills.md

skills:
  - name: load_dataset
    description: Reads a budget CSV dataset, validates columns, and checks for null values.
    input: input_path (str) to the budget CSV.
    output: list of dictionaries representing the rows in the CSV.
    error_handling: Raises FileNotFoundError if file is missing, and raises ValueError if expected columns are absent.

  - name: compute_growth
    description: Computes month-over-month growth for a specific ward and category, formatting formulas and handling nulls.
    input: ward (str), category (str), growth_type (str), and the dataset list.
    output: list of dicts with calculated growth percentage, the mathematical formula used, and status notes.
    error_handling: Refuses and prints/raises an error if ward or category is not specified, is "Any", or if growth_type is invalid/unspecified.

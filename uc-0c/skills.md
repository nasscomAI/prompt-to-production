skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the expected columns, and prints the total number of null rows along with details of which rows are null before returning.
    input: Path to the input budget CSV file (string)
    output: List of dictionaries representing the budget data rows (list[dict])
    error_handling: Raises FileNotFoundError if file does not exist, and ValueError if required columns are missing.

  - name: compute_growth
    description: Filters budget data for a specific ward and category, calculates growth (MoM or YoY) for each period, flags any null rows with notes, and outputs a table with the mathematical formulas.
    input: Budget data (list[dict]), ward name (string), category name (string), growth type (string)
    output: List of rows representing the growth calculations (list[dict])
    error_handling: Refuses calculation if growth type is missing, or if ward/category is ambiguous or missing. Prints null reasons instead of calculating for null rows.

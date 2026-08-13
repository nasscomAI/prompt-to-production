# skills.md — UC-0C Skills

skills:
  - name: load_and_validate_dataset
    description: Reads the input CSV budget file, validates that all required columns are present, and returns the contents as a structured list of dictionaries.
    input: Path to the budget CSV file.
    output: A list of row dictionaries.
    error_handling: Raises ValueError if the schema is invalid, or FileNotFoundError if the file does not exist.

  - name: compute_growth
    description: Filters rows by ward and category, sorts them chronologically, and computes MoM growth while detecting NULL actual spends, outputting formulas and formatted percentages.
    input: List of rows (dicts), ward (string), category (string), and growth_type (string).
    output: A list of computed result rows containing the calculated fields "formula" and "mom_growth".
    error_handling: Raises ValueError if filters result in zero matching rows, or if the growth type is unsupported.

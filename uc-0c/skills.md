skills:
  - name: load_dataset
    description: Reads the CSV dataset from the input path, validates that the required columns are present, and reports the null count and specific rows with null values before returning the data.
    input: Path to the input CSV file (string).
    output: List of dictionaries representing the rows of the CSV dataset.
    error_handling: Refuses and raises an error if the input file does not exist, is not a CSV, or lacks the required columns (period, ward, category, budgeted_amount, actual_spend, notes).

  - name: compute_growth
    description: Computes period-over-period growth (MoM or YoY) for the specified ward and category combination, preserving null flags and explaining formulas.
    input: Data list (list of dicts), ward name (string), category name (string), growth type (string, e.g., 'MoM' or 'YoY').
    output: List of dictionaries with calculated growth, formulas, and flagged null rows.
    error_handling: Refuses to aggregate across multiple wards/categories, and refuses if growth type is not specified or is invalid.

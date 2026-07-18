# skills.md

skills:
  - name: load_dataset
    description: Read the ward budget CSV dataset, validate that all required columns are present, and report the total count of null values along with the specific rows containing null actual_spend values and their reasons.
    input: Path to the CSV dataset (string).
    output: A validated dataset (e.g. pandas DataFrame or list of dictionaries) and a report of null values.
    error_handling: If the file is not found, raise an error. If required columns are missing, raise a validation error.

  - name: compute_growth
    description: Compute the growth rate per period for a specific ward and category using the specified growth type, showing the formula used for each row, and flagging any null rows with their reasons instead of calculating growth.
    input:
      ward: The ward name (string).
      category: The budget category (string).
      growth_type: The type of growth computation, e.g., MoM or YoY (string).
      dataset: The validated dataset.
    output: A per-period table (list of dictionaries or DataFrame) containing period, actual spend, computed growth, and the formula used, with null rows flagged.
    error_handling: If growth_type is not provided, refuse to compute and raise an error. If the ward or category does not exist in the dataset, raise an error.

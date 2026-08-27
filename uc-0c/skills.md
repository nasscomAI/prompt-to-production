skills:
  - name: load_dataset
    description: Reads a CSV dataset, validates columns, and reports null count and which rows contain nulls before returning the data.
    input: File path string to the CSV dataset.
    output: A list of dictionaries representing the dataset rows.
    error_handling: Exits if the file is missing or malformed. Flags and prints all null 'actual_spend' rows.

  - name: compute_growth
    description: Takes the dataset, a specific ward, category, and growth_type, returning a per-period table with the formula shown.
    input: Dataset list, ward string, category string, and growth_type string.
    output: A list of result dictionaries with computed growth and formula fields.
    error_handling: Refuses execution if ward or category implies aggregation, or if growth_type is missing. Outputs NULL growth for missing data points.

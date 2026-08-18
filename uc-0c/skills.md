# skills.md

skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, and reports null count and which rows contain nulls before processing.
    input: File path to the dataset CSV.
    output: A string representation of the loaded data and a summary of null values.
    error_handling: Raise an error if the file is missing or malformed.

  - name: compute_growth
    description: Takes the dataset, target ward, category, and growth_type, and computes a per-period table with formulas.
    input: Dataset text, ward name, category name, and growth type.
    output: A CSV formatted string containing Period, Actual Spend, Growth, and Formula/Notes.
    error_handling: Refuse to compute if growth_type is missing, or if requested to aggregate across wards/categories.

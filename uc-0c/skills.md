# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the schema, and identifies all rows with missing actual_spend data.
    input: File path to a budget CSV file.
    output: A validated dataset and a pre-processing report detailing null counts and specific null-containing rows.
    error_handling: If critical columns are missing or the file format is invalid, the system must trigger a 'DATA_INTEGRITY_ALERT' and stop.

  - name: compute_growth
    description: Calculates growth metrics for a filtered subset of data, providing mathematical transparency for every result.
    input: Parameters for 'ward', 'category', and 'growth-type' (e.g., MoM), along with the processed dataset.
    output: A table of growth results where each row explicitly shows the formula used and handles NULL values by reporting the source 'notes'.
    error_handling: If the requested growth-type is not provided or the ward/category filter yields no data, the skill must refuse the computation and request clarification.

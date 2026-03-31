# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads a CSV dataset, validates columns, and reports the null count and specific rows with missing values.
    input: Path to the dataset CSV file.
    output: Parsed data structure and a list of flagged null rows with their reasons.
    error_handling: Halts execution and warns the user if the expected CSV structure is invalid.

  - name: compute_growth
    description: Calculates growth for a given ward and category based on the specified growth type.
    input: Data structure, ward name, category name, and growth_type.
    output: A per-period table with the computed growth and the explicit formula shown.
    error_handling: Refuses the request if requested to aggregate across wards or categories, or if growth_type is missing.

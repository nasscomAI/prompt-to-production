# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads a budget CSV file, validates columns, and reports the null count and specific null rows before returning the data.
    input: File path to the .csv budget file.
    output: A validated dataset (e.g., list of dictionaries) and a summary report of any null values and their corresponding notes.
    error_handling: If the file is missing or malformed, raise an error. Ensure deliberate nulls in actual_spend are preserved as nulls, not converted to 0.

  - name: compute_growth
    description: Takes the validated dataset, ward, category, and growth_type, and returns a per-period table with calculated growth and formulas shown.
    input: Validated dataset, target ward, target category, and specific growth type (e.g., MoM).
    output: A per-period table (CSV format) containing the period, actual spend, computed growth metric, and the explicit formula used.
    error_handling: If growth_type is omitted or invalid, refuse execution. If asked to aggregate across wards/categories, refuse execution. If a row has a null actual_spend, output NULL for the metric and include the explanatory note instead of computing.

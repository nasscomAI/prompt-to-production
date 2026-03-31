# skills.md

skills:
  - name: load_dataset
    description: Reads a CSV dataset, validates columns, and reports the count and locations of any null values before returning the data.
    input: A string representing the file path to the CSV dataset.
    output: A JSON object containing the validated dataset rows and a report of any null values found.
    error_handling: If the file is missing or malformed, raise an appropriate specific error. If null values are found, they must be included in the output report.

  - name: compute_growth
    description: Takes specific ward, category, and growth type to return a per-period calculation table with the formula shown.
    input: The validated dataset, a target ward string, a target category string, and a growth_type string.
    output: A table (e.g., JSON array or CSV string) containing the computed growth per period, including the formula used, and flagging any null computations.
    error_handling: Refuse to compute and return an error message if the growth type is missing, or if the request requires unauthorized aggregation across wards/categories.

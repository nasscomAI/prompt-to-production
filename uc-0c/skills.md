skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates required columns, and reports null count and specific rows with nulls before returning the data.
    input: File path to the CSV dataset (string).
    output: Validated dataset (tabular data/dataframe) and a report of null counts/rows.
    error_handling: Refuses to proceed and raises an error if required columns are missing or if the file cannot be read.

  - name: compute_growth
    description: Calculates growth for a specific ward, category, and growth type, ensuring formulas are shown.
    input: ward (string), category (string), growth_type (string).
    output: A per-period table showing actual_spend, computed growth, and the formula used for each row.
    error_handling: Refuses and prompts the user if growth_type is missing; explicitly refuses if asked to aggregate across wards or categories without permission.

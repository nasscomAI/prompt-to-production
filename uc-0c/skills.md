skills:
  - name: load_dataset
    description: Reads CSV dataset, validates columns, and explicitly reports the count and reason for any null rows before returning the data.
    input: File path to the CSV file (string).
    output: Validated dataset structure, alongside a report of null counts and the specific rows containing them.
    error_handling: If the file is missing, unreadable, or missing required columns, refuse and explain the error.

  - name: compute_growth
    description: Calculates per-period growth for a specific ward and category based on a given growth type, displaying the used formula on every output row.
    input: Dataset, Ward (string), Category (string), and Growth Type (string, e.g., 'MoM').
    output: A per-ward, per-category table containing the computed growth values and the formulas used for each row.
    error_handling: Refuse to guess if 'growth_type' is not specified. Flag and refuse to compute growth on rows with null 'actual_spend', reporting the reason from the notes column. Refuse to aggregate across wards or categories unless explicitly instructed.

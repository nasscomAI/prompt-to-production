skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, and reports null count and which rows have nulls before returning.
    input: File path to the dataset (string).
    output: A validated dataset and a report of null counts and specific rows containing nulls (along with their reasons from the notes column).
    error_handling: Returns an error detailing missing columns if validation fails, or file not found error if the file path is invalid.

  - name: compute_growth
    description: Computes the requested growth type for a specific ward and category, returning a per-period table showing the formula used.
    input: Ward name (string), Category (string), and Growth type (string, e.g., MoM).
    output: A per-period table containing the computed growth values and the explicit formula used for every output row.
    error_handling: If the '--growth-type' is not specified or recognized, refuse to compute, do not guess, and return an error asking for clarification.

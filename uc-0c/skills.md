skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the required columns structure, and reports the null count and which rows contain null values before returning the data.
    input: File path to the dataset CSV (string).
    output: Dataframe containing the dataset, along with metadata about the total row count, and the count and specific locations (rows) of null values in `actual_spend`.
    error_handling: If the file is missing or schema is invalid, return an error. Logs and explicitly reports the null rows rather than silently skipping them.

  - name: compute_growth
    description: Takes a specified ward, category, and growth type to calculate growth, returning a per-period table with the exact formula used.
    input: Object containing `ward` (string), `category` (string), and `growth_type` (string).
    output: A per-period table output with computed growth percentages, alongside the explicit formula string used in every output row.
    error_handling: Refuse request and ask if `growth_type` is not specified. Do not guess the formula. Refuse to aggregate across multiple wards or categories. Flag null rows and do not compute growth for them.

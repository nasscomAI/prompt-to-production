skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates expected columns, and reports the count and specific locations of null values before returning the data.
    input: CSV file path (string).
    output: Validated dataset along with a report detailing any null values.
    error_handling: Raise an error if the file is missing or columns are invalid. Explicitly flag and report any null values found.

  - name: compute_growth
    description: Calculates the specified growth type (e.g., MoM) on a per-period basis for a specific ward and category, including the formula used.
    input: Dataset, ward (string), category (string), and growth_type (string).
    output: Per-period table containing actual spend, calculated growth, and the exact formula used for each row.
    error_handling: Refuse to compute if growth_type is not specified (do not guess). Refuse if asked to aggregate across multiple wards or categories. For null actual_spend rows, flag as "not computed" and output the null reason from the notes column.

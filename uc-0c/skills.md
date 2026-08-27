# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports the null count and specific rows containing nulls before returning the data.
    input: File path to the CSV (string).
    output: A list of dictionaries representing the parsed rows, along with a validation report of nulls.
    error_handling: Raise an error if the file is missing or malformed.

  - name: compute_growth
    description: Takes a filtered dataset (by ward and category) and a growth_type, checking for missing values and calculating the required growth metric for each period.
    input: Filtered data (list of dicts), ward (string), category (string), growth_type (string).
    output: A per-period table showing the period, actual spend, calculated growth, and formula used.
    error_handling: Return a polite refusal if growth_type is missing or if aggregation across wards/categories is attempted.

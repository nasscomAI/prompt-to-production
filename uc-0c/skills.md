# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and explicitly reports the count of null values and which rows they occur in before returning the dataframe.
    input: File path (string) to the budget CSV.
    output: A list of dictionaries representing the validated dataset (list).
    error_handling: Raise an error if required columns are missing.

  - name: compute_growth
    description: Computes either MoM or YoY growth for a strictly defined single ward and single category over time, injecting the formula text into the output.
    input: ward (string), category (string), growth_type (string: MoM or YoY), dataset (list).
    output: A list of result dictionaries containing ward, category, period, actual_spend, and growth.
    error_handling: If aggregating across wards or categories, or if growth_type is missing/unknown, raise an immediate RefusalException.

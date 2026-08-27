skills:
  - name: load_dataset
    description: Loads budget and actual spend data from the CSV file, validating columns and identifying any null actual_spend rows.
    input: The path to the CSV file (string).
    output: A list of dictionaries representing the validated CSV rows, with a list of flagged null actual_spend records.
    error_handling: If the file is missing or contains invalid columns, it raises an error. If null values are found in actual_spend, they are recorded with their reasons from the notes column.

  - name: compute_growth
    description: Calculates growth in actual spend for a specific ward and category using the requested growth type, showing the formula used.
    input: Validated rows (list of dicts), target ward (string), target category (string), and growth_type (string).
    output: A list of dictionaries containing period, actual spend, calculated growth percentage, and the math formula used.
    error_handling: Refuses to aggregate across wards or categories. If growth_type is not specified, or if a null actual_spend row is encountered during calculation, it flags the growth as NULL with notes rather than computing a numeric result.


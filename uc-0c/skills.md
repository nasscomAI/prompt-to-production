skills:
  - name: load_dataset
    description: Read the CSV file, validate columns, and report null count and rows containing null actual_spend values.
    input: File path of the CSV file (string).
    output: A list of dictionaries representing the validated CSV rows.
    error_handling: Return an empty list or raise an error if required columns (period, ward, category, budgeted_amount, actual_spend) are missing.

  - name: compute_growth
    description: Take the loaded dataset, filter by the specific ward and category, check for the growth type, and compute the month-over-month growth showing formulas and flagging null values.
    input: The dataset list of rows, ward name (string), category name (string), and growth_type (string).
    output: A list of result dictionaries representing the growth table.
    error_handling: If ward or category are not specified or requested as "all", raise a RefusalException. If growth_type is not provided, raise a RefusalException.

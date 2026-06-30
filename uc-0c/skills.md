# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward_budget.csv file, validates expected columns, reports
      the count and identity of rows with null actual_spend, and returns
      the dataset for processing.
    input: >
      Path to the CSV file as a string.
    output: >
      A pandas DataFrame (or equivalent) with validated columns. Also
      prints a pre-report listing which rows have null actual_spend and
      their notes.
    error_handling: >
      If file does not exist, raise FileNotFoundError. If required columns
      (period, ward, category, budgeted_amount, actual_spend, notes) are
      missing, raise a clear validation error listing the missing columns.

  - name: compute_growth
    description: >
      Given a ward, category, and growth_type, computes per-period growth
      rates and returns a table with the formula displayed per row.
    input: >
      ward (string), category (string), growth_type (MoM or YoY), and the
      loaded dataset.
    output: >
      A DataFrame with columns: period, ward, category, budgeted_amount,
      actual_spend, growth_rate, formula. Rows with null actual_spend are
      included with growth_rate set to "NULL" and a null_reason column.
    error_handling: >
      If growth_type is not MoM or YoY, raise a ValueError. If ward or
      category does not exist in the data, return an empty DataFrame with a
      warning message.

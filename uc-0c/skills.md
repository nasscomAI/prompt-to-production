skills:
  - name: load_dataset
    description: >
      Reads the CSV dataset, validates required columns,
      and reports rows with null actual_spend values.
    input: >
      Path to CSV dataset containing municipal budget data.
    output: >
      List of dataset rows and list of rows with null values.
    error_handling: >
      If required columns are missing, raise an error and stop execution.

  - name: compute_growth
    description: >
      Computes per-period growth for a given ward and category
      using the selected growth method.
    input: >
      Filtered dataset rows, ward name, category name, growth type.
    output: >
      Table containing period, actual_spend, growth_percent,
      formula used, and notes for null rows.
    error_handling: >
      If actual_spend is null, flag the row and skip growth calculation.

skills:
  - name: load_dataset
    description: >
      Reads the budget CSV file, validates the expected columns, identifies and reports
      any null values in the actual_spend column along with their reasons from notes.
    input: >
      - file_path: string — absolute or relative path to the CSV dataset.
    output: >
      A list of dicts representing the rows. Prints a report to stdout highlighting the
      total number of nulls and listing the specific rows (period, ward, category, reason)
      that contain nulls.
    error_handling: >
      If the file is missing or malformed, raise an exception. If the notes column is
      missing for a null row, report the reason as 'No reason provided'.

  - name: compute_growth
    description: >
      Computes the requested growth metric (MoM or YoY) for a specific ward and category,
      showing the formula used in each row. Handles null values transparently by outputting
      'NULL' instead of computing a value.
    input: >
      - data: list of dicts from load_dataset.
      - ward: string — the specific ward name.
      - category: string — the specific category.
      - growth_type: string — either 'MoM' or 'YoY'.
      - output_path: string — path to write the output CSV.
    output: >
      Writes a CSV file to output_path containing:
      period, ward, category, actual_spend, growth_type, growth_value, formula, notes.
      If a required parameter (ward, category, growth_type) is missing or asks for aggregation
      without explicit override, raises a ValueError with the exact RICE refusal message.
    error_handling: >
      If growth_type is not provided, refuse execution.
      If ward or category is not specified or implies aggregation (e.g., 'All'), refuse execution.
      If previous period data is missing (e.g., first month), output 'n/a' for growth.
      If current or previous period actual_spend is null, output 'NULL' for growth.

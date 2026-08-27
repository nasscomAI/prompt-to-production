skills:
  - name: load_dataset
    description: Reads the input CSV file, validates columns, and reports null counts and rows.
    input: Path to the CSV file (string).
    output: Validated dataset with null row details (dictionary).
    error_handling: >
      - If the file is missing or unreadable, return an error message.
      - If required columns are missing, return an error specifying the missing columns.
      - If the dataset contains invalid data types, return an error highlighting the problematic rows.
      - If any row contains null values, flag the row and include the null reason from the notes column in the error report.
      - If encoding issues are detected (e.g., misinterpreted characters), normalize the dataset to fix encoding errors.

  - name: compute_growth
    description: Computes growth for a specific ward and category based on the specified growth type.
    input: Ward (string), category (string), growth_type (string: 'MoM' or 'YoY').
    output: Per-period growth table with formulas explicitly shown alongside the calculated results (list of dictionaries). The output must strictly adhere to the per-ward, per-category structure.
    error_handling: >
      - If the ward or category is invalid, return an error specifying the issue.
      - If the growth_type is missing or unsupported, refuse and ask for clarification.
      - If null rows are present, flag them and include the null reason in the output.
      - Ensure that the formula used in every output row is explicitly shown alongside the result.
      - Refuse to compute if the output structure deviates from the per-ward, per-category requirement.

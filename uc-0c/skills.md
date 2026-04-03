skills:
  - name: load_dataset
    description: Reads the budget dataset CSV, validates columns, and reports null count and which rows before returning.
    input: File path to the CSV file (string).
    output: Validated dataset (dataframe/object) with a report on the number of nulls and their specific row locations.
    error_handling: Halts execution if required columns are missing and strictly flags rows with null actual_spend before proceeding.

  - name: compute_growth
    description: Takes a specified ward, category, and growth type, and returns a per-period table with the calculated growth and formula shown.
    input: Ward (string), category (string), and growth_type (string, e.g., MoM).
    output: A per-period table (dataframe/object) containing the calculation results and a column displaying the applied formula.
    error_handling: Refuses to compute and requests user input if growth_type is not provided. Skips computation for flagged null rows.

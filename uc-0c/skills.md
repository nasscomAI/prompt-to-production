skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates expected columns, and actively reports the total null count and specific rows with nulls before returning the data table.
    input: File path to the target CSV dataset.
    output: Validated dataset structured as a table, along with an explicit report of null value counts and their respective row details.
    error_handling: Refuses to process further if columns are incorrectly formatted. Flags the presence of null values before any processing.

  - name: compute_growth
    description: Computes growth metrics for a specific ward and category over time based on an explicit growth type, documenting the formula.
    input: Validated dataset table, target ward (string), target category (string), and an explicit growth_type parameter.
    output: Per-period table containing the computed growth metrics for the requested ward and category, including the explicit formula shown in each row.
    error_handling: Instructed to refuse and ask if `growth_type` is not specified. Prevents silent fallbacks by refusing any attempts to aggregate without explicit request.

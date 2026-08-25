skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates the schema, and reports any identified null values in actual_spend before proceeding.
    input: File path to a CSV containing budget and spend data by ward, category, and period.
    output: A validated list of data rows or a pandas-like structure; reports null count and reasons from the notes column.
    error_handling: Refuses to continue if the actual_spend column has silent nulls that aren't accounted for in the notes.

  - name: compute_growth
    description: Calculates growth (MoM or YoY) for a specific ward and category combination, ensuring zero-aggregation and explicit formula visibility.
    input: Data list, ward name, category name, and growth type (MoM/YoY).
    output: A per-period growth table containing the original spend, the calculated growth percentage, and the formula used.
    error_handling: Refuses to compute if growth_type is missing or if the request asks for cross-ward/cross-category aggregation.

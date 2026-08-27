skills:
  - name: load_dataset
    description: Reads the provided budget CSV file, validates the target columns, and identifies any missing data.
    input: File path to the budget CSV.
    output: The parsed data structure, along with a report detailing the null count and pinpointing which rows have null actual_spend values.
    error_handling: Refuses to process further if file is missing, logging an explicit error to the user.

  - name: compute_growth
    description: Computes the specified period-over-period growth for a specific ward and category.
    input: The validated dataset, target ward, target category, and specific growth_type (e.g., MoM, YoY).
    output: A per-period table showing the computed growth and the exact formula used for every row.
    error_handling: Automatically flags null value periods and reports reasons without applying the computation. Refuses to compute if growth_type is not provided.

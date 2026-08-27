skills:
  - name: load_dataset
    description: Load and validate the municipal budget dataset.
    input: CSV file path.
    output: Structured dataset rows.
    error_handling: If required columns are missing, return an error.

  - name: compute_growth
    description: Calculate month-over-month growth for a ward and category.
    input: Filtered dataset rows and growth type.
    output: Growth table containing period, spend, growth value and formula.
    error_handling: If actual_spend is null, mark row as NULL_FLAGGED.
skills:
  - name: load_dataset
    description: Reads a budget CSV file, validates the presence of required columns, and identifies rows with null values.
    input: Path to the ward_budget.csv file.
    output: A validated dataset object and a summary of null rows found with their reasons.
    error_handling: Validates column types and reports missing mandatory fields before processing.

  - name: compute_growth
    description: Calculates growth metrics for a specific ward and category over time, handling nulls as per enforcement rules.
    input: Parameters including ward name, category, and growth_type (MoM/YoY).
    output: A table of results for each period, including the spend, growth percentage, and the formula applied.
    error_handling: Returns a clear "NULL - [Reason]" entry for periods where spend data is missing, instead of attempting a calculation.

# Skills

skills:
  - name: load_dataset
    description: Read ward budget CSV data, validate required columns, and report null actual_spend rows.
    input: Path to ward_budget.csv.
    output: List of validated rows with parsed numeric values and null indicators.
    error_handling: Raise an error for missing columns or invalid data values.

  - name: compute_growth
    description: Compute growth for a single ward/category and return a row-level table.
    input: Filtered dataset rows plus growth_type ("MoM" or "YoY").
    output: List of rows including period, actual spend, prior spend, growth, formula, and flags.
    error_handling: For null rows, preserve the null reason and skip numeric growth calculation.

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates strictly against the ward/category schema, and identifies deliberate null values in actual spend.
    input: Path to the budget CSV file.
    output: A validated dataset object and a pre-processing report listing all detected null rows and their reasons.
    error_handling: Fail if schema columns are missing; explicitly list and flag rows with null actual spend before any computation.

  - name: compute_growth
    description: Calculates Month-over-Month (MoM) or Year-over-Year (YoY) growth for a specific ward and category, preserving per-period granularity.
    input: Ward name, category name, and growth type (MoM or YoY).
    output: A table showing period, actual spend, calculated growth, and the formula used for calculation.
    error_handling: Refuse all-ward aggregations; refuse computation if growth type is missing; skip null rows and report them as flagged.

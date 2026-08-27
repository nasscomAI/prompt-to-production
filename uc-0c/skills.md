skills:
  - name: load_dataset
    description: Reads the raw budget CSV, validates columns, and reports exactly how many and which specific rows contain null actual_spend values before returning.
    input: Filepath to the CSV dataset (e.g. `../data/budget/ward_budget.csv`).
    output: A validated dataset object/list alongside a strict pre-flight null report.
    error_handling: If input file is unreadable or malformed, raise a clear parsing error.

  - name: compute_growth
    description: Takes a specific single ward, category, and growth_type, and calculates growth explicitly showing the formula used on every row.
    input: Validated dataset rows filtered aggressively to a single ward and category, plus a growth_type string (e.g. 'MoM').
    output: A computed table matching the output format with added 'growth', 'formula', and 'flag' columns.
    error_handling: If required `--growth-type` is not given, halt completely. If actual_spend is null for a period, output NULL for growth and carry the reason into the flag column instead of substituting 0.

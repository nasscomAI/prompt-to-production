skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate the schema, and report null spend rows before analysis.
    input: CSV file path with period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: Validated dataset rows plus a report of null-count and null-row details.
    error_handling: If required columns are missing, periods are malformed, or the file cannot be read, stop with a clear validation error.

  - name: compute_growth
    description: Compute the requested growth series for one ward and one category and return a per-period table with formulas.
    input: Validated dataset rows, exact ward, exact category, and explicit growth_type value.
    output: Ordered per-period records containing actual spend, baseline value, formula string, growth result, status, and notes.
    error_handling: If the ward or category does not match exactly, or if a row needed for computation contains null spend, return flagged rows rather than guessing or imputing values.

skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate expected columns, parse numeric fields, and report null actual_spend rows.
    input: Path to `ward_budget.csv`.
    output: A list of normalized row dictionaries and a list of null-row summaries.
    error_handling: Raises a clear error if required columns are missing, period formatting is invalid, or numeric fields cannot be parsed.

  - name: compute_growth
    description: Compute growth metrics for a single ward and category using the requested growth type, while preserving formula details and null flags.
    input: A validated list of rows, plus `ward`, `category`, and `growth_type` strings.
    output: A per-period result table containing actual spend, previous baseline, growth percentage, formula text, status, and notes.
    error_handling: Raises a clear error if the ward/category combination is missing, the growth type is unsupported, or baseline data is unavailable for the requested growth type.

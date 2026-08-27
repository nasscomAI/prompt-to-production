skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates the required columns, and reports null rows before analysis.
    input: Path to the ward budget CSV file.
    output: Parsed dataset rows plus metadata about null actual_spend rows.
    error_handling: Reject missing columns or unreadable files, and never hide nulls or silently coerce blanks to zero.

  - name: compute_growth
    description: Computes per-period growth for one ward and one category using the requested growth type.
    input: Parsed dataset rows, a ward, a category, and a growth type such as MoM.
    output: A per-period table showing actual spend, growth result, status, and formula.
    error_handling: Refuse missing growth type or multi-ward aggregation requests, and mark rows as flagged when current or previous actual_spend is null.

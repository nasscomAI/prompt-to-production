skills:
  - name: load_dataset
    description: Read the ward budget CSV, validate required columns, and report null actual_spend rows before returning data.
    input: Path to ward_budget.csv file.
    output: Validated dataset with null report listing which rows have missing actual_spend and their notes.
    error_handling: Reject files with missing required columns; report all null rows before any computation.

  - name: compute_growth
    description: Compute month-over-month growth for a specific ward and category, returning a per-period table with formula shown.
    input: Ward name, category name, growth type (MoM), and validated dataset.
    output: CSV table with columns period, ward, category, actual_spend, previous_spend, growth_pct, formula, flag.
    error_handling: Flag null actual_spend rows instead of computing; refuse all-ward or all-category aggregation.

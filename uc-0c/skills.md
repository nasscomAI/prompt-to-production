skills:
  - name: load_dataset
    description: >
      Reads the CSV dataset, validates required columns, filters by ward and
      category, and reports all null actual_spend rows before computation.
    input: >
      CSV file path as string. Expected columns: period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      List of validated row dictionaries for the requested ward and category,
      sorted by period, plus metadata about null rows.
    error_handling: >
      Raises an error if required columns are missing, file is unreadable,
      ward/category has no rows, or null rows are detected.

  - name: compute_growth
    description: >
      Computes month-over-month growth for each valid row using the previous
      period actual_spend.
    input: >
      List of filtered dataset rows, ward string, category string,
      growth_type string (must be MoM).
    output: >
      Per-period table rows containing period, ward, category,
      actual_spend, growth_percentage, formula_used, and status.
    error_handling: >
      Refuses unsupported growth types, skips growth calculation for null rows,
      and flags division-by-zero or missing previous values explicitly.

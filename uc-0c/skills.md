skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports null count and details before returning.
    input:
      type: str
      format: path to the input CSV file
    output:
      type: list of dicts
      format: rows of the dataset
    error_handling:
      missing_file: Raise FileNotFoundError if input path doesn't exist.
      empty_rows: Log and skip empty rows, validating columns 'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', and 'notes'.

  - name: compute_growth
    description: Takes ward, category, and growth_type, and calculates period-over-period growth with formula tracking.
    input:
      type: dict
      format: contains keys 'ward', 'category', 'growth_type', and 'data'
    output:
      type: list of dicts
      format: output rows containing period, ward, category, budgeted_amount, actual_spend, growth_rate, formula, and status_notes
    error_handling:
      missing_parameters: Refuse calculation if ward, category, or growth_type is missing.
      null_actual_spend: Flag the row with status_notes from the source notes, leaving growth_rate and formula empty.

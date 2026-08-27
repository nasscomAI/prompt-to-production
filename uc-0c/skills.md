skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, and detects null actual_spend rows before computation.
    input: Path to a CSV file supplied through --input.
    output: A list of validated row dictionaries plus a list of rows where actual_spend is null.
    error_handling: Returns clear errors for missing files, missing headers, missing required columns, or empty datasets.

  - name: compute_growth
    description: Computes per-period growth for exactly one ward and one category using the requested growth type.
    input: Dataset rows, exact ward, exact category, and growth_type.
    output: CSV-ready rows with period, ward, category, actual spend, previous spend, growth, formula, and notes.
    error_handling: Refuses missing or unsupported growth types, refuses unmatched ward/category filters, marks null or invalid comparisons as NOT_COMPUTED, and never aggregates across wards or categories.

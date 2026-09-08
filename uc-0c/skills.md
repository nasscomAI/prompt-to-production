skills:
  - name: load_dataset
    description: Reads the municipal budget CSV file, validates required columns, audits data integrity, and identifies all null actual_spend rows and notes.
    input: File path to CSV dataset (string, e.g. path to ward_budget.csv).
    output: Dictionary containing loaded records, list of valid wards, list of valid categories, and list of identified null rows.
    error_handling: Raises FileNotFoundError if CSV missing, or ValueError if required schema columns (period, ward, category, budgeted_amount, actual_spend, notes) are absent.

  - name: compute_growth
    description: Computes period-over-period growth for a specified ward and category, preserving null row flags, showing calculation formulas for every period, and saving results to CSV.
    input: Dataset records, ward name, category name, growth_type (MoM or YoY), output CSV path.
    output: Writes formatted CSV containing period, ward, category, budgeted_amount, actual_spend, growth_type, growth_pct, formula, and notes.
    error_handling: Refuses execution if ward or category is missing or invalid, or if growth_type is not provided. Halts propagation across null values with explicit reason notation.

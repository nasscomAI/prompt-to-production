skills:
  - name: load_dataset
    description: Loads budget CSV data, validates ward and category filters, identifies null actual_spend rows, and extracts note reasons.
    input: CSV file path (ward_budget.csv), target ward string, and target category string.
    output: Filtered list of row dictionaries and null row diagnostic details.
    error_handling: Refuses un-scoped global requests, missing required parameters, or invalid wards/categories.

  - name: compute_growth
    description: Computes period-over-period growth (MoM) for filtered rows, generating formula strings and null flags.
    input: Filtered row data and growth_type string ('MoM').
    output: List of formatted output rows containing period, ward, category, budgeted_amount, actual_spend, mom_growth_pct, formula, and notes.
    error_handling: Handles null actual_spend rows by marking growth as FLAGGED and documenting notes; refuses execution if growth_type is missing.

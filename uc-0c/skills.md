skills:
  - name: load_dataset
    description: Loads the budget CSV dataset, validates schema, and identifies all null rows in actual_spend before any computation.
    input: file path (string, expected: ../data/budget/ward_budget.csv)
    output: pandas dataframe + null report (list of rows with period, ward, category, and null reason from notes column)
    error_handling: raise explicit errors for missing file, invalid format, or missing required columns; do not proceed if validation fails

  - name: validate_inputs
    description: Validates that ward, category, and growth_type are provided and strictly defined before computation.
    input: ward (string), category (string), growth_type (string: MoM or YoY)
    output: validation status (True if valid, otherwise raises Exception)
    error_handling: raise clear errors if any input is missing, invalid, or ambiguous (e.g., "overall", "all wards", or unspecified growth_type)

  - name: compute_growth
    description: Computes per-period growth (MoM or YoY) strictly for a single ward and category without aggregation, while handling null values explicitly.
    input: dataframe, ward (string), category (string), growth_type (MoM or YoY)
    output: structured table with columns [period, ward, category, actual_spend, previous_spend, growth_percentage, formula_used, null_flag]
    error_handling: 
      - raise error if growth_type is invalid
      - refuse computation if multiple wards or categories are detected (no aggregation allowed)
      - detect null current or previous values and flag them instead of computing
      - handle division by zero safely without crashing
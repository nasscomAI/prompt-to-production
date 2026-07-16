# skills.md

skills:
  - name: load_dataset
    description: >
      Reads ward_budget.csv, validates expected columns and data types, and reports the
      count of null actual_spend values and their row locations.
    input: path to CSV file (string)
    output: a list of dictionaries with keys: period, ward, category, budget_amount, actual_spend, notes
    error_handling: raises descriptive error if file is missing, columns mismatch, or date cannot be parsed

  - name: compute_growth
    description: >
      Given a ward and a category, computes per-period growth according to the specified
      growth type (MoM or YoY) using actual_spend. Attaches the formula used in a
      separate column. Null rows are not computed but flagged.
    input: load_dataset output as data list; ward string; category string; growth_type string (MoM or YoY)
    output: a list of dicts with period, actual_spend, growth_value, formula, and null_flag
    error_handling: returns an error string if growth_type is missing or not recognized; rows with
      null actual_spend are included in the output with null_flag populated by the notes reason

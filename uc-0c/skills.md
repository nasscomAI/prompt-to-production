# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Loads the budget CSV and validates structure, then reports null count and which rows before returning the data.
    input: File path string pointing to a UTF-8 encoded ward_budget.csv file.
    output: Tuple of (rows list, null_report_str) where null_report_str lists each row with null actual_spend and its reason from notes.
    error_handling: If the file is missing or has wrong column names, raise FileNotFoundError or ValueError. If actual_spend values are non-numeric, convert to float and report conversion failures.

  - name: compute_growth
    description: Takes a scoped dataset (single ward, single category, sorted by period) and growth_type, then returns a per-period table with growth values and formulas shown.
    input: Filtered list of rows (ward+category), growth_type string (MoM or YoY), and set of null_periods for this scope to flag.
    output: List of dicts with columns period, actual_spend, growth_value, growth_percentage, formula, null_flag. If no valid data, raise error.
    error_handling: If growth_type is invalid, raise ValueError. If the ward-category combo has no rows, raise KeyError. If a row has null actual_spend, set growth_value and growth_percentage to blank and flag it.

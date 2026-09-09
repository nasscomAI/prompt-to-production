skills:
  - name: load_dataset
    description: Reads and parses the ward budget CSV dataset, validating columns and identifying all null actual_spend rows and reasons.
    input: File path to input CSV (ward_budget.csv).
    output: Dictionary containing parsed dataset rows, total row count, and list of null row details.
    error_handling: Raises FileNotFoundError if CSV missing, or ValueError if required schema columns (period, ward, category, budgeted_amount, actual_spend) are missing.

  - name: compute_growth
    description: Calculates per-period MoM growth for a specified ward and category while embedding formula strings and flagging null rows.
    input: Parsed dataset, ward name, category name, and growth_type ('MoM').
    output: List of output row dictionaries containing period, ward, category, budgeted_amount, actual_spend, growth_pct, formula_used, and notes.
    error_handling: Refuses calculation if growth_type is missing/unsupported, or if requesting all-ward aggregation without parameters, flagging null rows cleanly without throwing errors.

# skills.md

skills:
  - name: load_dataset
    description: Reads the input CSV file, validates standard columns, and identifies and logs any rows with null actual spend.
    input: Path to budget CSV file.
    output: List of dictionaries representing the budget data rows.
    error_handling: Raise error if files or columns are missing.

  - name: compute_growth
    description: Filters data by ward and category, and calculates growth (MoM or YoY) for each period, flagging null rows and showing formulas.
    input: Data list, ward name, category name, growth type (MoM or YoY).
    output: Table containing period, actual_spend, growth_rate, formula, notes.
    error_handling: Refuse execution if parameters are missing or if aggregation across wards is attempted.

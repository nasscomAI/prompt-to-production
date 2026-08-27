# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, validates required columns, and reports null count with specific row details before returning structured data.
    input: File path (string) to ward_budget.csv containing columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: Dictionary containing: validated DataFrame, null count (integer), list of null rows with details (period, ward, category, notes), and validation status.
    error_handling: If required columns are missing, raise ValueError with specific missing columns. If file cannot be read, raise FileNotFoundError. Always report null details before proceeding.

  - name: compute_growth
    description: Computes growth rates for a specific ward-category combination using specified growth type, showing formulas and flagging null values.
    input: Dictionary from load_dataset, plus ward name (string), category name (string), and growth_type ('MoM' or 'YoY').
    output: CSV-compatible list of dictionaries with columns: period, ward, category, actual_spend, previous_spend, growth_rate, formula_used, null_flag. Each row shows the calculation formula and flags null values with notes.
    error_handling: If ward-category combination has no data, return empty list with warning. If growth_type is invalid, raise ValueError. For null values, set growth_rate to 'Must be flagged — not computed' and include notes. Never aggregate across wards or categories.

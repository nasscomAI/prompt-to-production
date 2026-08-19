skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns, identifies null actual_spend rows, and returns clean structured ward budget data.
    input: File path to ward_budget.csv.
    output: A tuple of (list of data rows, list of identified null rows with notes).
    error_handling: Raises FileNotFoundError if CSV missing; reports invalid headers or missing mandatory fields.

  - name: compute_growth
    description: Calculates per-period budget growth for a specific ward and category using the requested growth metric (MoM or YoY), capturing formulas and flagging uncomputable null periods.
    input: Filtered dataset rows, target ward name, target category name, and growth_type (MoM/YoY).
    output: Structured growth result table containing period, ward, category, budgeted_amount, actual_spend, growth_type, growth_percentage, formula, notes, and flag.
    error_handling: Refuses execution if growth_type is missing or if requested to aggregate across all wards/categories.

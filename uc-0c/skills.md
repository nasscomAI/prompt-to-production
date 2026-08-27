# skills.md
skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates columns, reports null count and row indices
    input: Path to ward_budget.csv
    output: List of dicts with period, ward, category, budgeted_amount, actual_spend, notes
    error_handling: Raise ValueError if required columns missing or file not found

  - name: compute_growth
    description: Computes MoM growth for specific ward + category, flagging nulls
    input: Dataset list, ward string, category string, growth_type (MoM/YoY)
    output: List of {period, actual_spend, growth_pct, formula, notes}
    error_handling: Raise ValueError if ward/category not found; flag nulls with notes
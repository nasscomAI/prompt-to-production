skills:
  - name: load_dataset
    description: Reads ward budget CSV, validates schema columns, identifies null actual_spend rows, and extracts note annotations.
    input: Path to ward_budget.csv dataset.
    output: Structured dataset object with validated records and pre-indexed null row alerts.
    error_handling: Raise error if dataset file is unreadable or missing required schema columns.

  - name: compute_growth
    description: Computes period-over-period growth (MoM or YoY) for a target ward and category, generating a detailed report with formulas and null flags.
    input: Dataset object, target ward name, target category name, and growth_type ('MoM' or 'YoY').
    output: A CSV dataset table containing period, ward, category, budgeted_amount, actual_spend, growth_rate, formula_used, and notes.
    error_handling: Refuse execution if ward or category is empty/all-encompassing, or if growth_type is omitted.

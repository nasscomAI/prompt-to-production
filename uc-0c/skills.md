skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates required column schemas, and identifies/reports all null actual_spend rows and associated notes before passing data downstream.
    input: File path string to input budget CSV file (e.g., ../data/budget/ward_budget.csv).
    output: A validated dataset object containing loaded records, list of total rows, and detailed log of flagged null actual_spend records.
    error_handling: Raises FileNotFoundError if CSV missing, ValueError if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing.

  - name: compute_growth
    description: Computes per-period growth rates (MoM or YoY) for a specific ward and category while explicitly flagging null values and recording exact mathematical formulas for every row.
    input: Validated dataset records, target ward string, target category string, and growth type string (MoM or YoY).
    output: Structured list of per-period result records including period, ward, category, budgeted_amount, actual_spend, growth_percent, formula_used, and notes/status flags.
    error_handling: Refuses calculation if growth type is missing/invalid or if aggregation across multiple wards/categories is requested; flags missing actual_spend or missing baseline actual_spend values with appropriate note reasons.

# skills.md — UC-0C Skills Specification

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates expected columns, detects null actual_spend rows, and reports the count and specific null rows with reasons before calculation.
    input: CSV file path (string, e.g. path to ward_budget.csv).
    output: Parsed rows, list of identified null records with period, ward, category, and notes.
    error_handling: Raises FileNotFoundError if CSV missing; validates required columns (period, ward, category, budgeted_amount, actual_spend, notes).

  - name: compute_growth
    description: Calculates growth rate (MoM or YoY) for a specific ward and category; reports formulas, flags null rows, and prevents cross-ward aggregation.
    input: Filtered rows for specific ward and category, growth_type string ('MoM' or 'YoY').
    output: Table/list of records with period, ward, category, budgeted_amount, actual_spend, growth_rate, formula, and status/notes.
    error_handling: Refuses if ward or category is 'All' or unspecified without explicit aggregation directive; refuses if growth_type is missing; flags rows where prior or current value is null.

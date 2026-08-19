skills:
  - name: load_dataset
    description: Reads the budget CSV, validates column structure, and identifies null values before processing.
    input: File path (string) to the ward_budget.csv source.
    output: A list of dict containing period, ward, category, budgeted_amount, actual_spend, and notes.
    error_handling: Report the total null count and specific rows with missing actual_spend before returning. Raise error if columns are missing.

  - name: compute_growth
    description: Calculates month-over-month (MoM) or year-over-year (YoY) growth per ward and category.
    input: List of records (dicts), ward (string), category (string), and growth_type (string).
    output: A list of dict including period, actual_spend, computed_growth (string), and formula used (string).
    error_handling: Refuse to compute growth for rows with null actual_spend and include the 'notes' reason in the output instead. Refuse all-ward aggregation.

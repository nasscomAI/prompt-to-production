# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and identifies rows with missing spend values.
    input: Path to `ward_budget.csv`
    output: A DataFrame or list of records, with a printed summary of null rows identified in `actual_spend`.
    error_handling: Refuses if the file is missing or contains invalid column headers (expected: period, ward, category, budgeted_amount, actual_spend, notes).

  - name: compute_growth
    description: Calculates growth (MoM or YoY) for a specific ward and category while enforcing data granularity.
    input: Ward name, budget category, growth-type (MoM/YoY), and the loaded dataset.
    output: A table including Actual Spend, Growth Percentage, and the specific Formula used; null rows are flagged with their reason from the notes.
    error_handling: Refuses to calculate if a growth-type is not provided or if asked for aggregated ward-level totals.

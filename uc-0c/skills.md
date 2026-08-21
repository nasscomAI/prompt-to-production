# skills.md — UC-0C Budget Growth Analysis

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the presence of required columns, and identifies all null actual_spend rows and their associated notes.
    input: Path to ward_budget.csv.
    output: A clean dataset accompanied by a report of null entries and their reasons.
    error_handling: Stop and report if required columns (period, ward, category, actual_spend) are missing.

  - name: compute_growth
    description: Calculates growth percentages (MoM) for a specific ward and category while embedding the formula in the output and bypassing null rows.
    input: Ward name, Category name, Growth type (MoM), and the validated dataset.
    output: A CSV-formatted table with columns: Period, Actual Spend, MoM Growth, and Formula.
    error_handling: If input parameters (ward/category) do not exist in the data, or if growth type is missing, return a refusal message.

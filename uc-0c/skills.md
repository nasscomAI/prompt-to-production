# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates mandatory columns, and reports all null entries with their reasons.
    input: Path to the `ward_budget.csv` file (string).
    output: A validated data structure and a detailed report of identified null rows.
    error_handling: Errors out if mandatory columns (period, ward, category, budgeted_amount, actual_spend) are missing.

  - name: compute_growth
    description: Calculates period-over-period growth for a specific ward/category combination, providing formulas for each result.
    input: Ward name, Category name, Growth type (MoM/YoY), and the loaded dataset.
    output: A per-period table containing actual spend, growth values, and the calculation formulas.
    error_handling: Refuses to compute growth for periods with null data, instead returning the flagged reason from the source.

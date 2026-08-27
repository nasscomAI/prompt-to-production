# skills.md — UC-0C Budget Growth Analyst
skills:
  - name: load_dataset
    description: Reads budget CSV, validates required columns (period, ward, category, budgeted_amount, actual_spend, notes), and reports null count and details of the 5 deliberate null rows.
    input: File path to ward_budget.csv.
    output: Cleaned and validated dataset (e.g., Pandas DataFrame or List of dicts).
    error_handling: Reports missing columns and fails if the file cannot be read; explicitly lists every row where actual_spend is null before processing.

  - name: compute_growth
    description: Calculates growth (MoM/YoY) for a specific ward and category combination, returning a per-period table with formulas shown.
    input: Ward name, Category name, Growth type (MoM), and dataset.
    output: Table containing Period, Actual Spend, Growth Value, and Calculation Formula.
    error_handling: Refuses to compute if ward or category is missing or invalid; flags null actual_spend rows as "NOT COMPUTED - [Reason from notes]" instead of calculating.

skills:
  - name: load_dataset
    description: Reads ward budget CSV, validates columns, reports null count and which rows
    input: str - path to ward_budget.csv file
    output: list of dicts with period, ward, category, budgeted_amount, actual_spend, notes
    error_handling: If file not found or missing columns, raise FileNotFoundError with clear message

  - name: compute_growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown
    input: list of dicts, str ward, str category, str growth_type (MoM or YoY)
    output: list of dicts with period, actual_spend, growth_pct, formula, null_flag, null_reason
    error_handling: If growth_type not MoM or YoY, raise ValueError; skip null rows but flag them
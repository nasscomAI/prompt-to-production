# skills.md — UC-0C

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: str — file path to ward_budget.csv
    output: dict — keys: "data" (list of dicts), "null_rows" (list of dicts with null info)
    error_handling: If file not found or missing required columns, raises ValueError with message

  - name: compute_growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown.
    input: dict — keys: "data" (list), "ward" (str), "category" (str), "growth_type" (str: MoM or YoY)
    output: list of dicts — each with period, actual_spend, growth_pct, formula, flag
    error_handling: If ward/category not found, returns empty list. Null rows flagged with reason.

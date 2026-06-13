# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, reports null count and which rows are null before returning structured data.
    input: file_path (str) — path to ward_budget.csv
    output: dict with keys: data (list of dicts), null_rows (list of dicts with period/ward/category/notes), null_count (int), columns (list)
    error_handling: If file not found, raise FileNotFoundError. If expected columns missing, raise ValueError. Reports all nulls even if data is otherwise valid.

  - name: compute_growth
    description: Takes filtered ward + category + growth_type (MoM/YoY), returns per-period table with actual_spend, growth %, formula, and null flags.
    input: data (list of dicts), ward (str), category (str), growth_type (str: "MoM" or "YoY")
    output: list of dicts with keys: period, ward, category, actual_spend, growth_pct, formula, flag
    error_handling: If ward not found, raise ValueError. If category not found, raise ValueError. If growth_type not MoM/YoY, refuse with error message. Null actual_spend rows return growth_pct: NULL with flag containing null reason.

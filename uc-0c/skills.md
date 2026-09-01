# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, reports null count and which rows before returning data.
    input: Path to ward_budget.csv (CSV with columns period,ward,category,budgeted_amount,actual_spend,notes).
    output: List of dict rows with typed fields and null-flag; plus summary string stating null count and list.
    error_handling: If missing columns → raise ValueError with expected vs found; if file not found → FileNotFoundError; if nulls present → log to stderr and include notes reason, never impute.

  - name: compute_growth
    description: Takes ward + category + growth_type and filtered rows, returns per-period table with formula shown for each growth value.
    input: Filtered rows for single ward+category (sorted by period), growth_type string (MoM or YoY).
    output: List of dicts with period, ward, category, budgeted_amount, actual_spend, growth_pct, formula, notes.
    error_handling: If growth_type missing → REFUSAL; if ward/category not found → REFUSAL with available values; if actual_spend null → growth N/A and formula "NULL: flagged — <notes>"; if previous period null → formula notes previous null; never aggregates across groups.

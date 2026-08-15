# skills.md — UC-0C Ward Budget MoM Growth Analyzer

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates the required columns, and reports the count and identity of every NULL actual_spend row before any computation.
    input: input_path (str) — path to ward_budget.csv
    output: list of row dicts with actual_spend parsed as float or None
    error_handling: Missing file or missing required columns exits with a clear error; unparseable spend values are treated as NULL and reported with the row.

  - name: compute_growth
    description: Computes per-period MoM growth for exactly one ward + one category, emitting formula, flag, and notes per row; refuses aggregation or unsupported growth types.
    input: rows (list), ward (str), category (str), growth_type (str)
    output: list of output row dicts (period, actual_spend, prev_actual_spend, growth_pct, formula, flag, notes)
    error_handling: Refuses 'all'/'any'/empty ward or category values and unknown growth types with an explicit message; rows with NULL spend or NULL previous spend are flagged NULL_SPEND / NO_PREV_PERIOD and never yield a growth number.
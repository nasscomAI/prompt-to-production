# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates the expected columns, and reports null actual_spend rows before any computation.
    input: Path to ward_budget.csv.
    output: A list of row dicts (period, ward, category, budgeted_amount, actual_spend, notes) plus a printed report of every row where actual_spend is null, with its period/ward/category/notes.
    error_handling: If a required column is missing from the header, raises a clear error naming the missing column instead of proceeding with partial data.

  - name: compute_growth
    description: Computes MoM or YoY growth in actual_spend for one ward + one category, per agents.md.
    input: Loaded rows, a ward name, a category name, and growth_type (MoM or YoY) — growth_type has no default.
    output: A per-period list of {period, actual_spend, growth_pct, formula, flag}, sorted by period, restricted to the requested ward + category only.
    scope_rule: Never includes rows from any other ward or category. If ward/category filtering yields zero rows, raises rather than returning an empty table silently.
    null_rule: A period whose actual_spend is null gets growth_pct blank and flag set to the notes-column reason; the period immediately after a null also cannot compute MoM against it, so that transition is flagged too, not silently skipped.
    error_handling: growth_type outside {MoM, YoY} raises with the two valid values named.

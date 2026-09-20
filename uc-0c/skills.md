# skills.md — UC-0C Municipal Budget Growth Analyzer

skills:
  - name: load_dataset
    description: Read ward_budget.csv, validate columns, and report null actual_spend rows before any math.
    input: CSV path (period, ward, category, budgeted_amount, actual_spend, notes expected).
    output: Validated row list with actual_spend parsed as float or None, plus a null report of {period, ward, category, notes} for every blank actual_spend.
    error_handling: Missing file raises FileNotFoundError; missing required column raises ValueError naming it; blank actual_spend becomes None with notes reason kept, never zero-filled or replaced by budgeted_amount.

  - name: compute_growth
    description: Compute per-period MoM or YoY growth for exactly one ward and one category with formula shown.
    input: Validated rows plus ward (exact string), category (exact string), growth_type (MoM or YoY only).
    output: Table rows of period, ward, category, actual_spend, growth_pct, formula, status where each computed row shows its formula and each null-involved row is flagged with the notes reason and blank growth.
    error_handling: Missing/unknown ward, category, or growth_type refuses with an explicit error (growth_type must be asked for, never guessed); no aggregation across wards/categories; YoY with no prior-year data yields flagged rows, not invented values.

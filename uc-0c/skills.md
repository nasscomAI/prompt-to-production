# skills.md — UC-0C Ward Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates the expected columns, and reports every null actual_spend row before returning data.
    input: file path (str) to a CSV with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: list of row dicts (actual_spend parsed to float or None), plus a printed null report listing each null row's period, ward, category, and reason from the notes column.
    error_handling: Unreadable file or missing expected columns → exits with a clear error naming what is wrong. Null actual_spend is preserved as None — never silently dropped, zero-filled, or interpolated.

  - name: compute_growth
    description: Computes per-period growth for exactly one ward + one category with the formula shown on every row.
    input: rows from load_dataset, ward (str), category (str), growth_type (must be 'MoM').
    output: ordered list of result rows (period, ward, category, actual_spend, formula, growth_pct, flag) — one per period; null periods and the period after them carry growth_pct=NOT_COMPUTED with the reason.
    error_handling: Ward or category not present in data → exits listing the valid values. growth_type missing or not MoM → refuses (YoY impossible: single-year dataset). Aggregation requests ('all' wards/categories) → refuses per agents.md rule 1.

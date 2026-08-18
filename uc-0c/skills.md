# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates its columns, and reports the null count and exactly which rows are null (period/ward/category/reason) before any computation happens.
    input: input_path (str) — path to ward_budget.csv with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      A list of row dicts (parsed: period as str, ward/category as str,
      budgeted_amount as float, actual_spend as float or None, notes as
      str) PLUS a printed/returned null report: total null count and, for
      each null row, its period/ward/category/notes reason.
    error_handling: >
      If required columns are missing, raises a clear error naming which
      column is missing rather than failing later with a KeyError deep in
      the growth computation. Never silently treats a null actual_spend as
      0 or drops the row from the returned dataset -- the row stays in the
      dataset with actual_spend=None so downstream code must explicitly
      handle it.

  - name: compute_growth
    description: Takes a loaded dataset plus one ward, one category, and one growth_type (MoM or YoY), and returns a per-period table with the formula shown for every row.
    input: >
      dataset (from load_dataset), ward (str -- resolved exact, then
      case-insensitive, then unambiguous substring; refuses rather than
      guessing if zero or multiple wards match), category (str, resolved
      the same way), growth_type (str, must be exactly "MoM" or "YoY" --
      no default).
    output: >
      A list of per-period row dicts: period, actual_spend (or "NULL"),
      comparison_period, growth_pct (float, or "NULL"), formula (str
      showing the exact arithmetic), null_reason (str, blank unless this
      period or its comparison period is null).
    error_handling: >
      Refuses (raises with a clear message) if ward or category does not
      exist in the dataset, if growth_type is missing or not one of
      MoM/YoY, or if the caller passes no ward/category at all (signalling
      an attempt at cross-ward aggregation). Never falls back to
      aggregating across wards/categories as a "helpful" default.

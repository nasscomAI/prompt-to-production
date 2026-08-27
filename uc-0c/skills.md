# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates its columns, and reports the null count and exactly which rows are null before any computation.
    input: >
      path (str) — path to ward_budget.csv with columns period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      The list of row dicts, plus a null report: count of null actual_spend rows
      and, for each, its period/ward/category and the reason taken from the notes
      column. Raises if any required column is missing.
    error_handling: >
      Missing required columns raise a clear error. Null actual_spend values are
      not dropped or coerced to zero — they are surfaced in the null report and
      carried through so downstream computation can flag them.

  - name: compute_growth
    description: Computes per-period growth for ONE ward + ONE category, showing the formula on every row and flagging nulls.
    input: >
      rows (from load_dataset), ward (str), category (str), growth_type
      ("MoM" or "YoY"). Ward/category matching is dash-insensitive.
    output: >
      A per-period table (one row per month) with columns ward, category, period,
      budgeted_amount, actual_spend, growth_type, formula, growth_pct, flag. Each
      computed row carries its exact arithmetic; null and uncomputable rows carry
      a flag (NULL_INPUT / NOT_COMPUTED / NO_PRIOR_PERIOD / NO_PRIOR_YEAR_DATA)
      instead of a number.
    error_handling: >
      Refuses (raises) if growth_type is missing or if ward/category names a
      whole-dataset aggregation (ALL / *). Never uses a null endpoint in a
      calculation; the period following a null is flagged NOT_COMPUTED.

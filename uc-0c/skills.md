# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates the required columns, and reports the null actual_spend rows with their notes reasons before any computation.
    input: Path to ward_budget.csv (--input).
    output: List of dataset rows plus a list of the null actual_spend rows (period, ward, category, reason from notes).
    error_handling: Raises if the file is missing, unreadable, or missing required columns; prints a warning listing every null row so none is silently processed.

  - name: compute_growth
    description: Computes the requested growth type for exactly one ward and one category, returning a per-period table with the formula shown on every row.
    input: Rows for exactly one ward + one category, plus growth_type (MoM or YoY).
    output: Per-period rows with period, actual_spend, growth_pct, formula, and flag; never a single aggregated number.
    error_handling: Refuses if growth_type is missing or if values would aggregate across wards/categories; flags null rows with the notes reason instead of computing on them.

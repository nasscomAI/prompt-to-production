# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its columns, and reports the null count and rows before returning the data.
    input: Path to ward_budget.csv (period, ward, category, budgeted_amount, actual_spend, notes).
    output: A data list of rows plus a structured null report (period, ward, category, notes for every row where actual_spend is blank).
    error_handling: Raises if the file is missing or required columns are absent; still returns row data alongside the null report so computation can proceed after nulls are flagged.

  - name: compute_growth
    description: Takes the dataset, one ward, one category, and the growth type, and returns a per-period growth table with the formula shown in every row.
    input: Loaded dataset rows, a ward name, a category name, and a growth type (e.g. MoM).
    output: A per-period table with period, actual_spend, growth %, and formula — one row per period for the requested ward+category only.
    error_handling: Refuses if the growth type is unspecified or unsupported; never aggregates across wards or categories; never computes on null rows (those are flagged, not imputed).

# skills.md — UC-0C Ward Budget Growth Analyzer
# Generated from the RICE prompt and refined against app.py.

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates the required columns and reports the null count and the exact null rows with their reasons before returning.
    input: input_path (path to ward_budget.csv).
    output: tuple of the row list and the null actual_spend row list.
    error_handling: Missing required columns raise a clear ValueError; null rows are reported to stdout before any computation happens.

  - name: compute_growth
    description: Takes a ward, a category and a growth type and returns the per-period growth table with the formula shown in every row.
    input: row list, ward (string), category (string), growth_type (string).
    output: list of period rows with actual spend, previous period values, signed growth percentage, formula, applied formula, flag and notes.
    error_handling: NULL actual_spend rows are flagged NULL_ACTUAL_SPEND with the notes reason and never computed; the first period is flagged NO_PREVIOUS_PERIOD; a zero previous value produces a PREVIOUS_ZERO flag instead of a division-by-zero.
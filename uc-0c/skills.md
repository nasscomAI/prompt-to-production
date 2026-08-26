# skills.md — UC-0C Ward Budget Analyzer

skills:
  - name: load_dataset
    description: Reads budget CSV, validates required columns, and identifies all null actual_spend rows alongside their notes.
    input: File path to ward budget CSV (input_path).
    output: Validated dataset structure containing row records and a list of identified null spend rows.
    error_handling: Reports missing columns or unreadable rows, and isolates null rows without silently dropping or filling them.

  - name: compute_growth
    description: Takes ward name, category name, and growth metric type, and computes per-period growth rates with explicit formulas and null flags.
    input: ward (str), category (str), growth_type (str), and dataset object.
    output: Per-period growth table containing period, budgeted_amount, actual_spend, growth_rate, formula, and notes.
    error_handling: Refuses execution if growth_type is missing or if requested to aggregate across multiple wards/categories without explicit instructions.

# skills.md — UC-0C Municipal Budget Growth Analyzer

skills:
  - name: load_dataset
    description: Read the municipal budget CSV, validate the required columns, identify null actual_spend values, and report their rows and reasons before any calculation.
    input: Path to a CSV file containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: Validated dataset with the null count and details of every row where actual_spend is missing.
    error_handling: If the file is missing, required columns are absent, or the data is invalid, report the error clearly and do not perform calculations.

  - name: compute_growth
    description: Calculate per-period MoM or YoY actual-spend growth for exactly one requested ward and category while showing the formula used for every result.
    input: Validated budget dataset, one exact ward, one exact category, and an explicitly specified growth type of MoM or YoY.
    output: Per-period table containing period, ward, category, actual_spend, growth_type, previous_period, previous_actual_spend, formula, growth_percent, flag, and notes.
    error_handling: Refuse missing or invalid growth types, refuse cross-ward or cross-category aggregation, and flag null actual_spend values or missing calculation dependencies without estimating them.
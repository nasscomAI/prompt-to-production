# skills.md

skills:

  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports null actual_spend values and their reasons before analysis.
    input: Path to a CSV file containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: Validated structured dataset plus a report of all rows where actual_spend is null.
    error_handling: If the file is missing, required columns are absent, or the dataset cannot be parsed, stop processing and report the error.

  - name: compute_growth
    description: Calculates the requested growth type for the specified ward and category at the per-period level with the formula shown.
    input: Validated dataset, ward, category, and explicitly specified growth type.
    output: Per-period table containing ward, category, period, actual spend, formula, growth result, status, and null reason where applicable.
    error_handling: Refuse if growth type is missing or unsupported, refuse all-ward aggregation, and do not compute growth for rows with null actual_spend or a null comparison period.
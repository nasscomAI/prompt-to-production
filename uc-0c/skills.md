skills:
  - name: load_dataset
    description: Read the budget CSV and validate its structure before analysis.
    input: CSV file path; expected columns are period, ward, category, budgeted_amount, actual_spend, and notes.
    output: Validated dataset plus the total null actual_spend count and every affected row with its period, ward, category, and notes reason.
    error_handling: Refuse when the file is unreadable, required columns are missing, or values cannot be validated; never silently discard malformed rows.

  - name: compute_growth
    description: Compute growth for one explicitly selected ward and category using the requested growth type.
    input: Validated dataset, one ward, one category, and an explicit growth_type such as MoM.
    output: Per-period table for the selected ward/category containing actual spend, the formula used, and the computed growth result; null rows are flagged and not computed.
    error_handling: Refuse all-ward or all-category aggregation, refuse when growth_type is missing or ambiguous, and report null reasons from notes before calculation.

skills:
  - name: load_dataset
    description: Read the budget CSV, validate its schema, and identify missing actual spend values before analysis.
    input: A CSV file path; expected columns are period, ward, category, budgeted_amount, actual_spend, and notes.
    output: A validated table plus the total null actual_spend count and the period, ward, category, and notes for every null row.
    error_handling: Refuse to continue when the file is missing, unreadable, or missing an expected column; preserve blank actual_spend values and never infer replacements.

  - name: compute_growth
    description: Compute growth for one ward and one category while retaining one output row per period.
    input: A validated budget table, exactly one ward, exactly one category, and an explicitly selected growth_type such as MoM or YoY.
    output: A per-period table containing ward, category, period, actual_spend, growth_type, the formula used, and the computed result; null rows are flagged and have no computed growth.
    error_handling: Refuse all-ward or cross-category aggregation, refuse when growth_type is missing or ambiguous, and report null reasons from notes before skipping those calculations.
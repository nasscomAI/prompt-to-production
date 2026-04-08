# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates all expected columns are present, and reports null count and which rows contain nulls before returning the data.
    input: Path to the ward_budget.csv file.
    output: Validated dataset object plus a null report listing row indices, ward, category, period, and notes for each null actual_spend value.
    error_handling: If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, halt and report which columns are missing — do not proceed with partial schema.

  - name: compute_growth
    description: Takes a ward, category, and growth_type (MoM or YoY), computes period-by-period growth for that slice, and returns a table with the formula shown alongside each result.
    input: Ward name (string), category name (string), growth_type (MoM or YoY), and the validated dataset from load_dataset.
    output: Per-period table with columns: period, actual_spend, growth_value, formula_used. Null rows are flagged, not computed.
    error_handling: If growth_type is not MoM or YoY, refuse and ask the user to specify. If the ward or category is not found in the data, report it and do not return empty results silently.

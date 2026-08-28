skills:
  - name: load_dataset
    description: Reads the budget CSV, validates its required columns, and reports null actual_spend records before returning the rows.
    input: A readable CSV path containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: Validated CSV rows plus a null count and the period, ward, category, and notes reason for every null actual_spend row.
    error_handling: Raises a clear error when the file is unreadable, has no header, or is missing a required column.

  - name: compute_growth
    description: Produces a chronological per-period growth table for one ward and one category using the requested growth type.
    input: Validated dataset rows, one exact ward, one exact category, and an explicit growth_type.
    output: Per-period rows containing actual spend, MoM growth or a non-computation status, null reason where relevant, and the formula used for each computed result.
    error_handling: Rejects all-ward or all-category requests, unsupported or omitted growth types, missing selections, unmatched selections, and null values that would otherwise be silently calculated.

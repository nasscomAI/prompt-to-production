skills:
  - name: load_dataset
    description: Reads and validates the ward budget CSV before analysis.
    input: "CSV path with period, ward, category, budgeted_amount, actual_spend, and notes columns."
    output: "Validated list of rows plus a null count and the null rows with their notes."
    error_handling: "Rejects missing required columns or malformed numeric values and reports every blank actual_spend row instead of silently skipping it."

  - name: compute_growth
    description: Computes requested month-over-month growth for one ward and category.
    input: "Validated rows, one ward, one category, and an explicit growth_type of MoM."
    output: "Per-period CSV rows containing the formula, growth percentage, and null or unavailable status."
    error_handling: "Refuses missing or unsupported growth types, refuses all-ward or all-category requests, and flags null current or prior values without computing growth."

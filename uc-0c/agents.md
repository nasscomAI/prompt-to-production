# agents.md — UC-0C Budget Growth Calculator

role: >
  Budget growth calculator agent responsible for computing period-over-period spend growth for specific ward-category combinations.
  Operates on filtered data only; never aggregates across wards or categories without explicit instruction.

intent: >
  For a given ward, category, and growth metric (MoM or YoY), produce a per-period table showing actual spend, growth percentage, and the formula used.
  Output must be verifiable — every null flagged with reason, every growth calculation shown with formula.

context: >
  Agent receives a CSV with 300 rows (5 wards, 5 categories, 12 months), of which 5 have null actual_spend values.
  Agent must filter to EXACT ward + EXACT category match only. No cross-ward or cross-category aggregation.
  Must refuse if --growth-type is unspecified. Must flag all nulls before computing. Must show formula in every row.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed. For every request, filter to single ward + single category. Refuse with clear error if asked to aggregate."
  - "Before computing growth, scan for null actual_spend rows and flag each one with its notes reason. Do not skip nulls silently — report them explicitly."
  - "Every output row must show the formula: MoM = ((Current - Previous) / Previous) * 100 or YoY = ((Current - Previous Year) / Previous Year) * 100. Do not compute unless formula is shown."
  - "If --growth-type is not specified, refuse with a clear message asking the user to specify MoM or YoY. Never guess or pick a default."

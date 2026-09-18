# agents.md - UC-0C Number That Looks Right

role: >
  Analyze ward budget spending for an explicitly requested ward and category,
  calculate the explicitly requested growth type, and produce a transparent
  per-period result without silently changing the aggregation level or formula.

intent: >
  Produce a verifiable per-ward, per-category growth table in which the
  requested growth formula is shown for every computable row and missing
  actual_spend values are explicitly flagged rather than treated as zero or
  silently skipped.

context: >
  The agent may use only the supplied ward_budget.csv dataset and the parameters
  explicitly provided by the user. It must use the period, ward, category,
  actual_spend, and notes fields from the dataset. It must not invent missing
  values, infer a growth type, or introduce external data.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed; if an all-ward or cross-category aggregation is requested, refuse."
  - "The output must remain at the requested ward + category level and contain one row per period."
  - "Flag every row with a null actual_spend before computing growth and report the corresponding notes value."
  - "Never replace a null actual_spend with zero, an average, an estimate, or a value inferred from another period."
  - "If the previous period or current period required for growth is null, do not compute the growth result for that period; flag the missing value and its reason."
  - "Show the exact formula used in every computable output row alongside the growth result."
  - "If --growth-type is not specified, refuse rather than guessing MoM, YoY, or another formula."
  - "For MoM growth, calculate ((current actual_spend - previous actual_spend) / previous actual_spend) * 100."
  - "Do not silently substitute budgeted_amount for actual_spend when actual_spend is missing."
  - "If the requested ward or category does not exist in the dataset, report the error and do not fabricate a result."
  - "Do not add external explanations, assumptions, or data not contained in the dataset or explicit request."
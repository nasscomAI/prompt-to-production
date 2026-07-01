# agents.md — UC-0C Budget Growth Calculator

role: >
  A municipal budget growth calculator agent that computes spending growth rates
  for a specific ward and category combination. Its operational boundary is strictly
  per-ward, per-category analysis — it must never aggregate across wards or categories
  unless the user explicitly instructs it to do so.

intent: >
  Produce a per-period growth table for a single ward and category showing: period,
  actual_spend, previous period actual_spend, the growth formula used, and the computed
  growth percentage. Null actual_spend values must be flagged with their reason from the
  notes column and excluded from computation — never silently filled or skipped.

context: >
  The agent operates on the ward_budget.csv dataset containing 300 rows across 5 wards,
  5 categories, and 12 months (Jan–Dec 2024). The dataset contains 5 deliberate null
  actual_spend values. The agent must use only the data present in the CSV and the
  user-specified parameters (--ward, --category, --growth-type). It must not assume
  defaults for any of these parameters.

enforcement:
  - "Never aggregate across wards or categories unless the user explicitly instructs it. If asked for an all-ward or all-category total, the system must refuse and explain why."
  - "Before computing any growth rate, flag every row where actual_spend is null. Report the null reason from the notes column. Do not silently drop, zero-fill, or interpolate null values."
  - "Every output row must show the formula used alongside the result (e.g. 'MoM = (current - previous) / previous * 100')."
  - "If --growth-type is not specified by the user, the system must refuse and ask the user to specify it. Never silently default to MoM or YoY."

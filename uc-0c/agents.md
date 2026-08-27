# agents.md — UC-0C Budget Growth Calculator

role: >
  Budget Growth Calculation Agent. Loads ward budget CSV and computes month-over-month (MoM)
  or year-over-year (YoY) growth for specific ward + category combinations.
  Operational boundary: only processes the specified ward and category; never aggregates
  across wards or categories unless explicitly instructed.

intent: >
  Output is a per-period table with columns: period, actual_spend, growth_rate, formula, flag.
  Growth rate is a percentage (positive or negative). Formula shows the calculation method
  (e.g., "(19.7 - 14.8) / 14.8 * 100"). Null rows are flagged with reason from notes column.
  Output is verifiable: sum of all periods must equal actual_spend totals, and growth rates
  must match manual calculation.

context: >
  The agent may only read columns: period, ward, category, actual_spend, notes.
  Other columns (budgeted_amount) are not used for growth calculation.
  Excluded from computation: any request to aggregate across wards or categories.
  The agent must flag null actual_spend values before computing and report the null reason.

enforcement:
  - "Never aggregate across wards or categories — refuse if --ward or --category is 'All' or missing. Each output must be for exactly one ward and one category."
  - "Flag every null actual_spend row with the reason from the notes column. Do not compute growth for null rows."
  - "Show formula used in every output row: (current - previous) / previous * 100 for MoM, (current - previous_year) / previous_year * 100 for YoY."
  - "If --growth-type not specified or invalid, refuse and ask: please specify --growth-type MoM or YoY."
  - "Refuse computation if dataset has fewer than 2 periods for MoM or 13 periods for YoY."

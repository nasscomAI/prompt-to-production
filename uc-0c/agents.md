# agents.md — UC-0C Growth Calculator

role: >
  A per-ward, per-category budget growth calculator. It reads the ward budget
  CSV and, given exactly one ward, one category, and one growth type, returns a
  per-period growth table. It never aggregates across wards or categories and
  never guesses the growth formula.

intent: >
  A correct output is a CSV written to the requested path containing one row
  per period (month) for the single requested ward and category, each row
  showing the actual spend, the exact formula used, the computed growth
  percentage, and a null flag where the actual_spend was blank. Every null row
  is flagged with its reason from the notes column — never silently skipped.

context: >
  The agent may use only the budget CSV passed in. It must not assume growth
  types, aggregate over multiple wards or categories, or infer missing actual
  spend values. The growth formula must be the one explicitly requested via
  --growth-type.

enforcement:
  - "Refuse to aggregate across wards or categories — growth must be computed for exactly one ward and one category as given on the command line; if ward or category is missing or invalid, refuse with an error instead of computing."
  - "Flag every null actual_spend row before computing — output null_flag=YES with the reason from the notes column, and never compute a growth value for a null row."
  - "Show the formula used in every output row alongside the result (e.g. MoM = (A[t] - A[t-1]) / A[t-1] * 100)."
  - "If --growth-type is not specified or is not a supported value, refuse and exit with an error — never guess MoM or YoY silently."

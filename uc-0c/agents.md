# agents.md - UC-0C Ward Budget Growth Calculator

role: >
  Deterministic municipal budget calculation agent. The agent computes growth
  only within an explicitly selected ward and category using the formula named
  by the user.

intent: >
  Produce a per-period growth table for one ward/category pair with actual
  spend, previous period spend, the formula used, the computed growth percent,
  and flags for rows that must not be computed.

context: >
  The agent may use only the input CSV fields: period, ward, category,
  budgeted_amount, actual_spend, and notes. It must not infer missing spend,
  choose a formula silently, or aggregate across wards/categories unless a
  future requirement explicitly permits that behavior.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed by a supported mode; refuse all-ward or all-category requests."
  - "The user must provide one explicit ward and one explicit category."
  - "Flag every null actual_spend row before computing and report the null reason from the notes column."
  - "Show the formula used in every output row alongside the result or the reason it was not computed."
  - "If --growth-type is not specified, refuse and ask for a formula; never guess MoM or YoY."
  - "Rows with current null actual_spend, previous null actual_spend, or previous zero actual_spend must be flagged and must not compute growth."
  
  

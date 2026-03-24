# agents.md — UC-0C Budget Growth Calculator

role: >
  Municipal budget growth analysis agent for CMC ward-level expenditure data.
  Computes month-on-month (MoM) or year-on-year (YoY) growth for a single
  specified ward and category. Does not aggregate across wards or categories.

intent: >
  For a given ward, category, and growth type, produce a row-per-period table
  showing: period, actual_spend, growth_pct, and the formula used.
  Growth is computed as (current - prior) / prior × 100, rounded to one decimal.
  A correct output matches reference values: Ward 1 Roads July +33.1%, October −34.8%.

context: >
  Input: ward_budget.csv (300 rows). The agent restricts all calculations to
  the exact ward name and category name supplied. It must report null rows
  upfront and exclude them from growth calculations. Cross-ward or cross-category
  aggregation is never performed — that would produce a meaningless average.

enforcement:
  - "Scope is strictly per-ward per-category — the agent must refuse any request to compute growth across all wards or across all categories simultaneously"
  - "Null actual_spend rows must be detected, listed by name at the start of output, and excluded from the growth table — silently skipping nulls is a failure"
  - "The growth formula must be printed per row: '(current - prior) / prior × 100 = X%' — showing only a percentage without the formula is not acceptable"
  - "Ward names must match exactly including the em dash — using a hyphen instead of '–' will return wrong results and the agent must not silently return empty results; it must raise a clear error"
  - "Refuse to produce a single aggregate growth number for 'all wards' — respond with a scope error naming which ward and category are required"

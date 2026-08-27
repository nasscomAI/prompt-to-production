# agents.md

# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.

# Delete these comments before committing.

role: >
Ward budget growth analysis agent. The agent operates only on the supplied
ward_budget.csv dataset and computes growth at the explicitly requested ward
and category level, never as an all-ward or all-category aggregate unless that
aggregation is explicitly requested.

intent: >
Produce a verifiable per-ward per-category growth_output.csv table with one
output row per period for the requested ward, category, and growth_type. Each
row must include the source period, ward, category, actual_spend, growth
result or null flag, formula used, and enough comparison information for the
result to be independently checked.

context: >
Use only ../data/budget/ward_budget.csv and its columns: period, ward,
category, budgeted_amount, actual_spend, and notes. Treat blank actual_spend
values as nulls, not zeroes. Do not infer missing values, choose formulas
silently, combine wards or categories by default, or use external budget
assumptions.

enforcement:

- "Never aggregate across wards or categories unless explicitly instructed; refuse if asked."
- "Flag every null row before computing; report the null reason from the notes column."
- "Show the formula used in every output row alongside the result."
- "If --growth-type is not specified, refuse and ask; never guess."
- "The output must be a per-ward per-category table, not a single aggregated number."
- "Blank actual_spend values must be treated as NULL and must not be computed as zero."
- "Rows with NULL actual_spend must be flagged and not computed."
- "For Ward 1 – Kasba / Roads & Pothole Repair, 2024-07 must show actual_spend 19.7 and MoM growth +33.1%."
- "For Ward 1 – Kasba / Roads & Pothole Repair, 2024-10 must show actual_spend 13.1 and MoM growth -34.8%."
- "For Ward 2 – Shivajinagar / Drainage & Flooding, 2024-03 must be flagged as NULL and not computed."
- "For Ward 4 – Warje / Roads & Pothole Repair, 2024-07 must be flagged as NULL and not computed."

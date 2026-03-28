# agents.md
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: "UC-0C budget growth agent. Operates on ward_budget.csv and computes per-ward, per-category growth in one target ward/category at a time, with strict null handling and formula disclosure."

intent: "Given input CSV, ward, category, growth-type and output path, emit uc-0c/growth_output.csv as a per-period table for the specified ward/category, showing actual_spend, growth result, formula, and status; do not aggregate across wards/categories."

context: "Allowed data is only ../data/budget/ward_budget.csv rows and CLI parameters; no cross-ward/category aggregations, no external dataset usage. Must not infer missing growth-type parameter or compute ward-agnostic aggregates."

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — refuse when ward/category is all/any."
  - "Flag every row with null actual_spend before computing and include notes from notes column."
  - "Show formula used in every output row (e.g. MoM = (current - prior)/prior * 100)."
  - "If --growth-type is not specified, refuse and ask; do not guess."
  - "Output must be per-ward per-category not a single aggregated number."
  - "Must support reference check values: for Ward 1 – Kasba Roads & Pothole Repair 2024-07 19.7 +33.1% and 2024-10 13.1 -34.8%; null rows flagged."

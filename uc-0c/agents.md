# agents.md
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: >
  Calculate Month-over-Month (MoM) or Year-over-Year (YoY) growth metrics for a specific ward and budget category.
  Never aggregate across wards or categories. Refuse aggregation requests unless explicitly instructed.

intent: >
  Output a per-ward, per-category growth table with explicit formulas shown for each row.
  Verify against reference values: Ward 1 – Kasba / Roads & Pothole Repair / 2024-07 = +33.1% MoM;
  2024-10 = −34.8% MoM. Flag all null rows with reason before computing.

context: >
  Input: ward_budget.csv with 300 rows, 5 wards, 5 categories, 12 months (Jan–Dec 2024).
  5 rows have deliberately null actual_spend values (documented in README with reason in notes column).
  Allowed to use: specified ward name, category name, and growth_type parameter only.
  Excluded: aggregation across wards, aggregation across categories, guessing growth_type.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — refuse if asked"
  - "Flag every null row before computing — report null reason from the notes column"
  - "Show formula used in every output row alongside the result"
  - "If --growth-type not specified — refuse and ask, never guess"

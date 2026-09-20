# agents.md — UC-0C Municipal Budget Growth Analyzer

role: >
  Careful Python data analyst. Computes growth for exactly one requested
  ward and one category over time from ward_budget.csv. No cross-ward or
  cross-category math, no guessed formulas, no silent nulls.

intent: >
  Produce uc-0c/growth_output.csv: one row per period for the requested
  ward+category with actual_spend, growth value, formula text, and null
  status. Verifiable by: Ward 1 Kasba / Roads & Pothole Repair / MoM shows
  2024-07 +33.1% and 2024-10 -34.8%; the 5 null rows are flagged with notes
  reasons, never computed; missing ward/category/growth-type refuses.

context: >
  Allowed input: data/budget/ward_budget.csv columns period, ward, category,
  budgeted_amount, actual_spend, notes; plus CLI args --ward, --category,
  --growth-type (MoM or YoY). Exclusions: do NOT sum or average across wards
  or categories; do NOT substitute budgeted_amount for null actual_spend;
  do NOT infer growth_type when absent.

enforcement:
  - "1. Never aggregate across wards: filter rows to the exact --ward string only; test fails if any other ward appears in output."
  - "2. Never aggregate across categories: filter rows to the exact --category string only; test fails if any other category appears in output."
  - "3. If ward is missing or does not match any row, refuse with error naming the ward; test fails on guessed ward."
  - "4. If category is missing or does not match any row, refuse with error naming the category; test fails on guessed category."
  - "5. If growth-type is missing or not MoM/YoY, refuse and ask for it explicitly; never default; test fails on silent MoM/YoY choice."
  - "6. Identify null actual_spend rows before calculation and list them; test fails if a null row is computed."
  - "7. Never calculate growth when current or previous actual_spend is null; leave growth blank and flag NULL."
  - "8. Report the null reason from the notes column verbatim in the status field; test fails on generic null without reason."
  - "9. Show the formula beside every calculated result (MoM: (curr-prev)/prev*100 with values; YoY: (curr-same-month-prior-year)/prior*100); test fails on a result row without formula."
  - "10. Preserve the exact ward and category requested in every output row; test fails on altered ward/category strings."

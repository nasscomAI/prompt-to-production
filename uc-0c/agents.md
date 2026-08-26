# UC-0C — agents.md (Budget Growth)

## ROLE
You compute spending-growth figures for the City Municipal Corporation budget.
Officials make funding decisions from your numbers, so a number that "looks
right" but blends wards or hides a missing month is worse than no number.

## INPUT
ward_budget.csv — 300 rows · 5 wards · 5 categories · 12 months (2024-01 to
2024-12). Columns: period, ward, category, budgeted_amount, actual_spend, notes.
Exactly 5 actual_spend cells are deliberately null.

## CONSTRAINTS (hard rules)
1. Never aggregate across wards or categories unless explicitly instructed.
   A request for "all wards", "total", or "*" must be REFUSED, not answered.
2. Flag every null actual_spend row before computing, and report the null reason
   from the `notes` column. Never treat null as zero and never skip it silently.
3. Show the exact formula used in every output row, including which period the
   value is compared against.
4. If the growth type (MoM or YoY) is not specified, REFUSE and ask. Never guess.

## FORMULAS
- MoM growth % = (current_month − previous_month) / previous_month × 100
- YoY growth % = (current_month − same_month_last_year) / same_month_last_year × 100
A null on either side of the comparison => the row is flagged, not computed.

## ENFORCEMENT
- Ward/category equal to an "all"-type token raises a refusal before any maths.
- load_dataset prints all null rows and their reasons up front.
- compute_growth attaches the literal formula string to every computed row and
  emits "FLAGGED — not computed" where a value is null.
- --growth-type has no default; its absence triggers an explicit refusal.

## REFERENCE VALUES (must reproduce)
- Ward 1 – Kasba · Roads & Pothole Repair · 2024-07 = 19.7 -> MoM +33.1%
- Ward 1 – Kasba · Roads & Pothole Repair · 2024-10 = 13.1 -> MoM −34.8%
- Ward 2 – Shivajinagar · Drainage & Flooding · 2024-03 = NULL -> flagged
- Ward 4 – Warje · Roads & Pothole Repair · 2024-07 = NULL -> flagged
- Any all-ward request -> REFUSED

## OUTPUT
A per-ward, per-category table (one row per period) with actual_spend,
growth_type, growth_pct, the formula, and a note column for null reasons.

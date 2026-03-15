# agents.md — UC-0C Number That Looks Right

role: >
  Budget calculation engine that computes aggregated spend and budget totals per ward and per 
  category, maintaining strict scoping to prevent cross-ward or cross-category contamination. 
  Does not aggregate beyond requested scope. Handles null values explicitly.

intent: >
  A correct output is a per-ward per-category table with columns: ward, category, total_budgeted, 
  total_actual_spend, variance, null_count. Totals are verifiable by summing the input rows for 
  the specified ward and category only. Variance = total_budgeted - total_actual_spend. Null 
  counts are explicit (not silently treated as zero). Output covers exactly one ward and one 
  category per run, never aggregated across wards or categories.

context: >
  Agent receives: input CSV file, ward name, category name, and optional growth-type parameter. 
  Agent must read only rows matching the specified ward AND category. It must not aggregate 
  across different wards, different categories, or mix null/non-null rows. It must preserve 
  the date ordering (period field) for growth calculations. It must not interpolate missing 
  months or infer values for null actual_spend rows.

enforcement:
  - "Aggregation scope: Output is strictly per-ward per-category. Sum only rows where ward matches AND category matches. Never cross-sum different wards or categories."
  - "Null handling: Count null actual_spend rows separately. Display null_count in output. Do not treat nulls as zero. Do not exclude null rows. Document the reason from the 'notes' field."
  - "Variance calculation: variance = total_budgeted - total_actual_spend (where actual exists). If all actual_spend are null, output variance as null or explicitly state 'Cannot calculate: no spend data'."
  - "No interpolation: Month-over-month growth is calculated only if both months have non-null actual_spend. If prior or current month is null, output 'N/A' for that growth value. Never skip months or infer missing data."

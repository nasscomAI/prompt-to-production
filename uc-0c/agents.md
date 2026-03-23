# UC-0C Growth Calculator

role:
This agent computes growth metrics for budget data at a per-ward per-category level.

intent:
The output must be a table showing growth per period for a specific ward and category.

context:
Only the given dataset is allowed. No aggregation across wards or categories is permitted.

enforcement:
- Never aggregate across wards or categories
- Filter strictly by given ward and category
- Null values must be flagged and not used in calculations
- Growth formula must be shown for each row
- If growth-type is missing, do not compute

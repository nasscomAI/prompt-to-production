# UC-0A Skills

## classify_complaint
Input: one complaint row from CSV.

Process:
1. Read the description text.
2. Match keywords to determine category.
3. Check severity keywords to determine priority.
4. Generate a reason referencing the description text.
5. If ambiguous, set category to Other and flag NEEDS_REVIEW.

Output fields:
- complaint_id
- category
- priority
- reason
- flag


## batch_classify
Process:
1. Read input CSV file.
2. Apply classify_complaint to each row.
3. Collect results.
4. Write results to output CSV.
5. Continue processing even if one row fails.
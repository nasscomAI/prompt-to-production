# UC-0C Agents

## Budget Growth Analysis Agent

The agent must follow these rules:

1. Never aggregate data across wards or categories unless explicitly instructed.
   If the user asks for an all-ward or cross-category aggregation, refuse.

2. Always require a specific ward and category for growth analysis.

3. Always require an explicit growth type.
   Supported growth type:
   - MoM

4. If `--growth-type` is not specified, refuse to calculate growth.
   Never guess whether the user wants MoM or YoY.

5. Check for null actual_spend values before calculating growth.
   Every null row must be flagged and its reason from the `notes` column must be reported.

6. Do not calculate growth for a row whose current actual_spend is null.

7. Do not silently replace null values with zero or another value.

8. For MoM growth, use:
   ((current_month_actual_spend - previous_month_actual_spend)
   / previous_month_actual_spend) * 100

9. The first month has no previous month, so its growth must be marked as N/A.

10. Every output row must show the formula used alongside the result.

11. Output must remain at the per-ward, per-category, per-period level.
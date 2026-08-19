# UC-0C Skills

## load_dataset

Purpose:
- Read the budget CSV.
- Validate required columns.
- Report the number of rows.
- Detect null actual_spend values.
- Report every null row and its notes/reason.
- Return the validated dataset.

Required columns:
- period
- ward
- category
- budgeted_amount
- actual_spend
- notes

## compute_growth

Purpose:
- Calculate growth for one specific ward and category.
- Require an explicit growth type.
- Currently support MoM.

Inputs:
- dataset
- ward
- category
- growth_type

Behavior:
- Filter only the requested ward and category.
- Sort records by period.
- Do not aggregate.
- For MoM, compare each month's actual_spend with the previous month.
- If either required value is null, do not calculate growth.
- Show the null reason from notes.
- Show the formula used for every calculated row.

MoM formula:

((current_actual_spend - previous_actual_spend) / previous_actual_spend) * 100
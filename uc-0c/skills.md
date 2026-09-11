# UC-0C Skills

## load_dataset

Load the budget CSV and validate these columns:
- period
- ward
- category
- budgeted_amount
- actual_spend
- notes

Report every row where actual_spend is null before calculating growth.

For each null row, report the period, ward, category, and reason from the notes.

Do not invent or estimate missing actual_spend values.

## compute_growth

Inputs:
- ward
- category
- growth_type

Return a per-period table for the requested ward and category.

Rules:
1. Never aggregate across wards or categories.
2. Show the growth formula beside every calculated result.
3. If actual_spend is null, flag the row and do not calculate growth.
4. If growth type is missing, refuse to calculate and ask for it.
5. Do not guess missing values.
6. Preserve the requested ward and category exactly.
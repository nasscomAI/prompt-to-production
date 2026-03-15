# UC-0C Skills

## load_dataset

Loads the ward_budget.csv dataset.

Responsibilities:
- Validate required columns:
  period, ward, category, budgeted_amount, actual_spend, notes
- Identify rows where actual_spend is NULL
- Report the row and the reason from the notes column

Returns:
structured dataset

---

## compute_growth

Computes growth metrics.

Inputs:
- ward
- category
- growth_type

Rules:
- Filter dataset by ward and category
- Sort by period
- Compute Month-over-Month growth using:

MoM Growth =
(current_month_actual - previous_month_actual) / previous_month_actual * 100

- If current or previous value is NULL → do not compute
- Return "NULL — computation skipped"

Output:
table with
period | actual_spend | formula | growth_percentage

# Skills — UC-0C Number That Looks Right

## load_dataset
**Input:** `path` to ward_budget.csv
**Output:** list of row dicts
**Behavior:**
- Validates all required columns (period, ward, category,
  budgeted_amount, actual_spend, notes) are present; exits with an
  error if any are missing.
- Before returning, prints the total row count and every row with a
  null actual_spend, including its notes-column reason, to stderr.

## compute_growth
**Input:** rows (from load_dataset), ward, category, growth_type
**Output:** list of per-period dicts with period, actual_spend,
growth_pct, formula
**Behavior:**
- Filters to exactly one ward and one category - never aggregates.
- Exits with an error if the ward/category combination matches no rows.
- For growth_type=YoY: since the dataset covers only one calendar year,
  every row is marked growth_pct=N/A with an explicit note that YoY
  cannot be computed from this dataset.
- For growth_type=MoM: computes ((current - previous) / previous) * 100
  per period, in chronological order.
  - If the current period's actual_spend is null, growth is marked
    NULL with the notes-column reason shown in the formula field.
  - If the previous period's actual_spend is null, the current
    period's growth is also marked NULL (cannot compute across a gap),
    not silently computed against an older valid value.
  - The first period in the series always shows N/A (no prior period).

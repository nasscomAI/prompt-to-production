# agents.md — UC-0C: Number That Looks Right

## Agent Identity
**Name:** BudgetAnalysisAgent  
**Role:** Civic Budget Data Processor  
**UC:** UC-0C — Number That Looks Right

---

## Mission
Analyze ward-level budget data to compute year-on-year growth figures **strictly per ward and per category**. The agent must never silently aggregate across wards or blend categories. Every number in the output must be traceable to a single ward + single category combination.

---

## RICE Definition

### Result
Produce `growth_output.csv` containing:
- Ward name
- Budget category
- Budget allocated (current year)
- Budget allocated (previous year)
- Absolute change (current − previous)
- Percentage growth (rounded to 2 decimal places)
- A flag: `GROWTH`, `DECLINE`, or `NO_CHANGE`

### Input
- `data/budget/ward_budget.csv`
- Columns expected: `ward`, `category`, `year`, `amount`

### Constraints
1. Never aggregate across wards — each row in output maps to exactly one ward.
2. Never blend categories — each row maps to exactly one category.
3. If a ward+category pair has no previous-year entry, mark growth as `N/A`.
4. Do not invent or impute missing values.
5. Output must be sorted by ward, then category, then year (descending).

### Evaluation (CRAFT test)
- Run on `ward_budget.csv`
- Verify: no row in output covers more than one ward
- Verify: no row in output covers more than one category
- Verify: growth % formula = ((current - previous) / previous) * 100
- Verify: output file is named exactly `growth_output.csv`

---

## Failure Modes to Avoid
| Failure | Description | Fix Applied |
|---|---|---|
| Silent aggregation | Summing all wards together | Explicit `groupby(['ward','category'])` |
| Cross-category blending | Mixing road + water budgets | Strict per-category processing |
| Division by zero | Previous year = 0 | Guard clause, output `N/A` |
| Wrong year pairing | Comparing non-consecutive years | Sort by year, use `diff()` only within group |

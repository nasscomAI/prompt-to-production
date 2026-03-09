# UC-0C — Number That Looks Right · agents.md

## Agent Identity
- **Name:** BudgetGrowthAgent
- **Role:** Calculate per-ward, per-category budget growth from `ward_budget.csv`
- **Owner:** Gaddam Siddharth | City: Hyderabad

---

## Goal
Read `data/budget/ward_budget.csv` and produce `growth_output.csv` with correct growth % calculated **per ward per category only** — no cross-ward or cross-category aggregation.

---

## Failure Mode This UC Tests
**Silent aggregation** — computing a number that looks plausible but is wrong because totals were aggregated across wards or categories before computing growth.

---

## Enforcement Rules (CRAFT-refined)
1. Growth % = `((current_year - previous_year) / previous_year) * 100`
2. Calculation scope: **per row** (one ward + one category at a time)
3. Never aggregate across wards before computing growth
4. Never aggregate across categories before computing growth
5. Flag rows where `previous_year = 0` as `DIV_ZERO` instead of crashing
6. Round growth to 2 decimal places

---

## Inputs
| Field | Description |
|-------|-------------|
| `ward` | Ward identifier |
| `category` | Budget category (Roads, Water, etc.) |
| `previous_year` | Previous year budget (₹) |
| `current_year` | Current year budget (₹) |

## Outputs
| Field | Description |
|-------|-------------|
| `ward` | Passed through |
| `category` | Passed through |
| `previous_year` | Passed through |
| `current_year` | Passed through |
| `growth_pct` | Growth % rounded to 2dp, or `DIV_ZERO` |
| `growth_direction` | UP / DOWN / FLAT / DIV_ZERO |

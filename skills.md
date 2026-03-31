# UC-0C: The Number That Looks Right — skills.md

## Skill: ScopedBudgetAggregation

**Purpose:** Compute year-over-year budget growth strictly at the `(ward, category)` scope — never silently wider.

---

## Skill Definition

### Input
- A CSV file (`ward_budget.csv`) with at minimum these columns:
  - `ward` — name/ID of the municipal ward
  - `category` — budget category (e.g., Roads, Health, Education)
  - `year` — fiscal year (e.g., 2023, 2024)
  - `budget` — allocated budget amount (numeric)

### Output
- `growth_output.csv` with columns:
  - `ward` — ward name
  - `category` — budget category
  - `year_from` — base year
  - `year_to` — comparison year
  - `budget_from` — budget in base year
  - `budget_to` — budget in comparison year
  - `growth_pct` — percentage change (rounded to 2 decimal places)
  - `scope` — always `"per_ward_per_category"` for row-level data; `"city_total"` or `"category_total"` only when explicitly labelled
  - `flag` — `OK`, `DATA_MISSING`, `ZERO_BASE` (if base year budget is 0, growth % is undefined)

---

## Skill Rules (Enforced in Code)

1. **Group strictly by `(ward, category, year)`** — never drop any grouping level.
2. **Pivot years** — reshape so each `(ward, category)` row has one column per year.
3. **Compute growth only between consecutive years** — do not skip years.
4. **Flag before compute** — check for missing values BEFORE computing growth; set `flag = DATA_MISSING` and `growth_pct = None`.
5. **Label every aggregate** — if a city-wide total is added, it must have `ward = "ALL_WARDS"` and `scope = "city_total"`.
6. **No silent zeros** — `fillna(0)` is forbidden unless the source data explicitly records a ₹0 allocation.

---

## Skill: AnomalyDetector

**Purpose:** Flag rows where growth % is suspiciously high/low compared to ward peers.

### Rules
- If `growth_pct > 200%` → flag `HIGH_GROWTH_OUTLIER`
- If `growth_pct < -50%` → flag `LARGE_CUT_OUTLIER`
- These flags are additive — a row can have `OK|HIGH_GROWTH_OUTLIER`

---

## Skill: SummaryReporter

**Purpose:** Print a clean summary to stdout after generating `growth_output.csv`.

### Output format (stdout)
```
============================================================
  BudgetGuard — Ward Budget Growth Report
============================================================
  Wards analysed    : <N>
  Categories        : <list>
  Year range        : <min_year> → <max_year>
  Rows computed     : <N>
  Flagged rows      : <N> (DATA_MISSING: X | ZERO_BASE: Y | OUTLIERS: Z)
============================================================
  Top 3 fastest-growing (ward, category):
    1. <ward> | <category> : +XX.X%
    2. ...
  Top 3 largest cuts:
    1. <ward> | <category> : -XX.X%
============================================================
  Output saved → growth_output.csv
============================================================
```

# UC-0C — Skills Definition

## Skill: load_dataset

### Description
Loads a ward budget CSV file and filters it to a specific ward and category.

### Inputs
| Parameter | Type   | Required | Description                            |
|-----------|--------|----------|----------------------------------------|
| filepath  | string | yes      | Path to the ward_budget.csv file       |
| ward      | string | yes      | Ward name to filter (exact match)      |
| category  | string | yes      | Budget category to filter (exact match)|

### Output
A list of row dictionaries sorted by period, filtered to the specified ward and category.
Each row contains: period, ward, category, budgeted_amount, actual_spend (float or None), notes.

### Behaviour
- Read CSV with headers: period, ward, category, budgeted_amount, actual_spend, notes
- Filter rows where ward == specified ward AND category == specified category
- Convert actual_spend to float; treat empty/blank as None
- Sort by period ascending (lexicographic sort on YYYY-MM is correct)
- Return filtered, sorted rows

---

## Skill: compute_growth

### Description
Computes period-over-period growth rates for a filtered series of budget rows.

### Inputs
| Parameter   | Type   | Required | Description                                    |
|-------------|--------|----------|------------------------------------------------|
| rows        | list   | yes      | Filtered rows from load_dataset                |
| growth_type | string | yes      | "MoM" (month-over-month) or "YoY" (year-over-year) |

### Output
A list of result dictionaries with columns: period, ward, category, actual_spend, growth_pct, formula, flag.

### Behaviour
- For the first row: growth_pct = "", formula = "", flag = "" (no previous value)
- For a row where actual_spend is None:
  - growth_pct = ""
  - formula = ""
  - flag = "NULL - [notes value]"
- For a row where the previous row had actual_spend = None:
  - growth_pct = ""
  - formula = ""
  - flag = "PREV_NULL"
- For a normal row with valid current and previous actual_spend:
  - growth_pct = round(((current - previous) / previous) * 100, 1)
  - formula = "(current - previous) / previous * 100 = growth_pct%"
  - flag = ""
- Never aggregate across wards or categories
- If growth_type is not provided or invalid, raise an error

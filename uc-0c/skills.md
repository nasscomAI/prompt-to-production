# UC-0C Number That Looks Right — Skills

## Skills

### 1. Load Budget Data

- **name**: `load_budget_csv`
- **description**: Reads ward_budget.csv and returns list of row dicts.
- **input**: File path (str or Path)
- **output**: List of dicts with keys: period, ward, category, budgeted_amount, actual_spend, notes
- **error_handling**: Raise FileNotFoundError if missing; skip malformed rows, log count.

### 2. Parse Amount

- **name**: `parse_amount`
- **description**: Converts cell value to float; returns None for empty/invalid.
- **input**: Cell value (str or number)
- **output**: float or None
- **error_handling**: Empty, "Data not submitted", notes → None. Invalid numeric → None.

### 3. Calculate Totals

- **name**: `calculate_totals`
- **description**: Computes per-ward and per-category totals for budgeted and actual.
- **input**: List of parsed budget rows
- **output**: Dict with ward_totals, category_totals, period_totals, grand_total
- **error_handling**: Skip rows with None amounts; include only valid numeric rows.

### 4. Detect Suspicious

- **name**: `detect_suspicious`
- **description**: Flags rows where actual > budget by threshold (default 20%).
- **input**: Rows, threshold (float, default 1.2)
- **output**: List of flagged row dicts with reason
- **error_handling**: Skip rows with missing actual or budget.

### 5. Flag Inconsistencies

- **name**: `flag_inconsistencies`
- **description**: Identifies missing data, negative values, anomalies.
- **input**: List of rows
- **output**: List of inconsistency records
- **error_handling**: Handle all edge cases gracefully.

---

## Validation Rules

| Rule | Check |
|------|-------|
| Amount parsing | Empty → None; numeric string → float |
| Overspend threshold | actual > budget * 1.2 |
| Missing data | actual_spend empty or non-numeric |

---

## Example Inputs/Outputs

**Input** (row):
```
2024-06,Ward 2 – Shivajinagar,Roads & Pothole Repair,15.8,19.7,
```

**Output** (suspicious):
```json
{
  "period": "2024-06",
  "ward": "Ward 2 – Shivajinagar",
  "category": "Roads & Pothole Repair",
  "budgeted_amount": 15.8,
  "actual_spend": 19.7,
  "reason": "Overspend: 24.7% over budget"
}
```

---

**Input** (row with missing actual):
```
2024-03,Ward 2 – Shivajinagar,Drainage & Flooding,10.0,,Data not submitted by ward office
```

**Output** (inconsistency):
```json
{
  "period": "2024-03",
  "ward": "Ward 2 – Shivajinagar",
  "category": "Drainage & Flooding",
  "reason": "Missing actual_spend",
  "notes": "Data not submitted by ward office"
}
```

# UC-0C Financial Analysis Skills

## Defined Skills

### 1. `load_dataset`
- **Description**: Reads budget CSV file, validates schema, identifies null actual_spend rows, and returns validated dataset alongside a list of null records.
- **Input**: CSV file path.
- **Output**: Validated row objects + null summary audit log.

### 2. `compute_growth`
- **Description**: Filters dataset by specific ward and category, sorts by period, and calculates period-over-period growth while explicitly tagging null periods and printing calculation formulas.
- **Input**: Dataset, target ward, target category, growth type (`MoM` or `YoY`).
- **Output**: Growth results table with columns: `period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, `mom_growth_pct`, `formula_used`, `status_notes`.

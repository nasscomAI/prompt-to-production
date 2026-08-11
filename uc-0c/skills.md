# skills.md — UC-0C Number That Looks Right

## Skill: load_dataset
- **Input**: CSV file path (`ward_budget.csv`)
- **Process**: Read CSV, validate column schemas, identify all null rows in `actual_spend`, report null counts and notes before proceeding.
- **Output**: Clean dataset structure + list of flagged null records.

## Skill: compute_growth
- **Input**: Filtered dataset (by single `ward` and single `category`), `growth_type` (`MoM` or `YoY`).
- **Process**:
  1. Verify target ward and category are single, valid entities (refuse if All/Any or missing).
  2. Sort data chronologically by `period`.
  3. Calculate growth period over period using formula: `((Current - Previous) / Previous) * 100`.
  4. For periods with current or previous value as NULL, flag as `NULL_DATA (Reason: <notes>)` without computing invalid numbers.
- **Output**: Rows containing `period`, `ward`, `category`, `actual_spend`, `growth_type`, `growth_pct`, `formula`, `flag`.

# UC-0C Skills

## Skill: load_dataset
**Input:** Path to CSV file
**Output:** Pandas DataFrame + null report
**Logic:**
- Read CSV with pandas
- Validate columns: period, ward, category, budgeted_amount, actual_spend, notes
- Before returning: print count of null actual_spend rows and list each one (period, ward, category, reason from notes)
- Return DataFrame

## Skill: compute_growth
**Input:** DataFrame, ward (str), category (str), growth_type (str: MoM or YoY)
**Output:** Per-period table written to CSV with columns: period, ward, category, actual_spend, prev_spend, formula, growth_pct, null_flag, null_reason
**Logic:**
- Filter DataFrame to exact ward + category match
- For each row in chronological order:
  - If actual_spend is null: set null_flag=NULL_FLAGGED, null_reason from notes, skip growth calc
  - If previous row is also null: set growth_pct=SKIPPED (prev period null)
  - Otherwise: compute growth, show formula string, round to 1 decimal
- Write all rows to output CSV

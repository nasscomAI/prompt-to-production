# UC-0C Financial Analysis — Skills Definition

## Skill 1: `load_dataset`

**Purpose**: Reads the budget CSV file, validates the schema, and reports null `actual_spend` rows before returning the data.

**Input**: CSV file path.

**Output**: Tuple of (all_rows, null_rows) where:
- `all_rows`: List of row dictionaries with an added `actual_spend_val` field (float or None).
- `null_rows`: List of (row_number, row_dict) tuples for rows with missing spend data.

**Behaviour**:
- Validates that expected columns exist: `period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, `notes`.
- Identifies null values: empty string, "null", "none", or whitespace-only.
- Prints a null audit report to stdout listing each null row's period, ward, category, and reason from `notes`.

**Error handling**: Exits with error if file not found or required columns are missing.

---

## Skill 2: `compute_growth`

**Purpose**: Filters data by ward and category, then computes period-over-period growth rates with full formula transparency.

**Input**: Dataset rows, target ward, target category, growth type (`MoM`), output file path.

**Output**: CSV file with columns: `period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, `mom_growth`, `formula_used`, `status_notes`.

**Behaviour**:
- Filters to exact ward + category match.
- Sorts by `period` ascending.
- For each row:
  - If `actual_spend` is null → outputs `NULL (Flagged)` with reason from notes.
  - If first row after a null → outputs `N/A (Baseline)` since previous period is unknown.
  - Otherwise → computes `((current - previous) / previous) × 100` and records the formula.
- Refuses to run if `--ward` is "all" or `--growth-type` is missing.

**Error handling**: Prints error and exits if ward/category yields zero matching rows.

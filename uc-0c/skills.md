# UC-0C — skills.md (Budget Growth)

## skill: load_dataset
**Purpose:** Read the budget CSV, validate it, and surface nulls before use.
**Input:** path to ward_budget.csv.
**Output:** (rows, null_rows). Prints total row count, null count, and each
null row with its reason from the `notes` column.
**Logic:**
1. Read with DictReader; assert the 6 required columns exist.
2. Collect every row whose actual_spend is blank.
3. Print them up front so nulls are never invisible.

## skill: compute_growth
**Purpose:** Per-period MoM or YoY growth for ONE ward + ONE category.
**Input:** rows, ward, category, growth_type (MoM|YoY).
**Output:** list of per-period dicts: actual_spend, growth_pct, formula, note.
**Logic:**
1. Refuse if ward or category is an "all"-type token (no cross aggregation).
2. Refuse if growth_type is not MoM or YoY.
3. Filter to the one ward+category, sort by period.
4. For each period, compare against the period `lag` back (1 for MoM, 12 for YoY).
5. If current or comparison value is null -> emit "FLAGGED — not computed".
6. Else compute (cur − prev)/prev × 100 and attach the literal formula string.

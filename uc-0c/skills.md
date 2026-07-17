# UC-0C Skills

## load_dataset

**Input:** Path to ward_budget.csv

**Output:** Tuple of (all_rows, null_rows)

**Logic:**
1. Read CSV with DictReader.
2. Validate required columns: period, ward, category, budgeted_amount, actual_spend, notes.
3. Identify rows where actual_spend is empty/null.
4. Report null count and details (period, ward, category, reason from notes).
5. Return all rows and null rows separately.

**Enforcement:**
- Exit with error if required columns are missing.
- Always report nulls BEFORE any computation begins.

---

## compute_growth

**Input:** rows, null_rows, ward (str), category (str), growth_type (str), output_path (str)

**Output:** CSV file with per-period growth table including formula

**Logic:**
1. Validate growth_type is "MoM" or "YoY" — refuse otherwise.
2. Filter rows to the specified ward + category only.
3. Sort by period.
4. For each period:
   - If current period is null → flag, do not compute.
   - If prior period is null → flag, do not compute.
   - If first period → mark as baseline.
   - Otherwise → compute: (current - previous) / previous * 100.
5. Write output with columns: period, ward, category, actual_spend, growth_pct, formula, flag.

**Enforcement:**
- Never aggregate across wards or categories.
- Show formula for every computed row.
- Flag every null explicitly with reason.

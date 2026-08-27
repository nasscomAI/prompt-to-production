# skills.md — UC-0C Skill Contracts

## Purpose
Define reliable, reusable skills for UC-0C so growth calculations are transparent, non-aggregated by default, and safe around null data.

## Skill: `load_dataset`

### Objective
Load `../data/budget/ward_budget.csv`, validate schema, and report null data issues before any growth computation.

### Inputs
- `input_path` (string): path to CSV file

### Required Validations
1. File exists and is readable.
2. Required columns exist:
   - `period`
   - `ward`
   - `category`
   - `budgeted_amount`
   - `actual_spend`
   - `notes`
3. `period` format is `YYYY-MM`.
4. `actual_spend` is numeric or null.

### Required Null Reporting (before compute)
- Detect all rows where `actual_spend` is null.
- Return:
  - `null_count`
  - `null_rows` (array of objects with `period`, `ward`, `category`, `notes`)
- Do not suppress nulls.

### Output Contract
Return an object with:
- `dataframe` (or table object)
- `row_count`
- `column_count`
- `null_count`
- `null_rows`
- `status` (`ok` | `error`)
- `reason` (required when `status = error`)

---

## Skill: `compute_growth`

### Objective
Compute growth for a scoped slice (`ward` + `category`) and return per-period rows with explicit formulas.

### Inputs
- `dataframe` (table from `load_dataset`)
- `ward` (string)
- `category` (string)
- `growth_type` (string; required, e.g., `MoM`, `YoY`)

### Guardrails
1. **No implicit aggregation**
   - Scope must stay at `ward + category + period` unless explicitly authorized.
   - If asked for global aggregation across wards/categories, refuse.
2. **No growth-type guessing**
   - If `growth_type` is missing, refuse.
3. **Null-safe computation**
   - If current or required comparison `actual_spend` is null, do not compute growth for that row.

### Required Refusals
- Missing growth type:
  - `Refused: --growth-type is required. Please specify a growth type (e.g., MoM or YoY).`
- Unsafe aggregation:
  - `Refused: Aggregating across wards/categories is disabled by UC-0C guardrails unless you explicitly authorize that aggregation scope.`

### Formula Transparency
Every computed row must include a `formula` field.

For MoM, use:
- `((current_actual_spend - previous_actual_spend) / previous_actual_spend) * 100`

### Output Contract
Return per-period rows with:
- `period`
- `ward`
- `category`
- `actual_spend`
- `growth_type`
- `formula`
- `growth_percent`
- `status` (`computed` | `flagged_null` | `not_computed`)
- `reason` (required when status != `computed`)

### Status Rules
- `computed`: growth value successfully computed.
- `flagged_null`: `actual_spend` is null for current row.
- `not_computed`: comparison period missing/null/invalid (e.g., no previous month for MoM).

---

## UC-0C Verification Targets
- `Ward 1 – Kasba` + `Roads & Pothole Repair` + `2024-07` MoM ≈ `+33.1%`
- `Ward 1 – Kasba` + `Roads & Pothole Repair` + `2024-10` MoM ≈ `-34.8%`
- `Ward 2 – Shivajinagar` + `Drainage & Flooding` + `2024-03` must be `flagged_null`
- `Ward 4 – Warje` + `Roads & Pothole Repair` + `2024-07` must be `flagged_null`

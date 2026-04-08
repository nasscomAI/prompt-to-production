# agents.md — UC-0C Budget Growth Agent
## RICE Framework: Reach · Impact · Confidence · Effort

---

## Agent Identity

**Name:** BudgetGrowthAgent  
**Purpose:** Compute period-over-period spending growth for a specified ward and category from municipal budget data. Never aggregate, never guess, never silently skip nulls.

---

## RICE Prioritisation

| Rule | Reach | Impact | Confidence | Effort | RICE Score | Priority |
|---|---|---|---|---|---|---|
| Refuse cross-ward aggregation | All queries | Critical — prevents misleading totals | High (100%) | Low | 1000 | **P0** |
| Flag nulls before any computation | All queries with nulls | High — null silencing is the core failure mode | High (100%) | Low | 800 | **P0** |
| Show formula in every output row | All growth computations | High — auditability requirement | High (100%) | Medium | 600 | **P1** |
| Refuse if --growth-type omitted | Queries without explicit type | Medium — prevents silent wrong answers | High (100%) | Low | 500 | **P1** |
| Validate columns on load | Every CSV load | Medium — fails fast before bad state | High (100%) | Low | 400 | **P2** |

> RICE Score = (Reach × Impact × Confidence) / Effort.  
> P0 rules are blocking — the agent must not produce any output if violated.

---

## Enforcement Rules (Hard Stops)

### Rule 1 — Never Aggregate Across Wards or Categories
**Trigger:** `--ward` or `--category` is `all`, `*`, `total`, `aggregate`, or any alias implying a rollup.  
**Response:**
```
[REFUSED] Aggregation across wards or categories is not permitted.
          You must specify an exact --ward and --category.
          This system produces per-ward, per-category outputs only.
```
**Why it exists:** The naive failure mode is returning a single number for all wards combined. This produces a plausible-looking but meaningless figure.  
**Override:** None. The user must re-run with an explicit scope.

---

### Rule 2 — Flag Every Null Row Before Computing
**Trigger:** Any row where `actual_spend` is blank or empty string.  
**Response:** Print to stdout before any computation begins:
```
⚠  NULL ROWS (will be flagged, not computed):
   • <period> | <ward> | <category>
     Reason: <notes column value>
```
**What must NOT happen:**
- Treating null as 0 (inflates or deflates growth)
- Silently skipping the null row and computing the next pair
- Imputing with mean/median without explicit user instruction
- Omitting the null row from output

**In output CSV:** The null row must appear with `status = "NULL — not computed"` and `formula_used = "N/A (null actual_spend)"`.

---

### Rule 3 — Show Formula in Every Output Row
**Trigger:** Every computed growth value.  
**Required field in output:** `formula_used`  
**Format:** `(<current> − <prev>) / <prev> × 100 = <result>%`  
**Why:** Silent formula choice is the second core failure mode. YoY vs MoM produces radically different numbers; the formula column makes the choice auditable per row.

**Special cases:**
| Situation | formula_used value |
|---|---|
| First period (no prior) | `N/A (no prior period in dataset)` |
| Prior period is null | `N/A (prior period is null)` |
| Division by zero | `N/A (division by zero)` |
| Current period is null | `N/A (null actual_spend)` |

---

### Rule 4 — Refuse If `--growth-type` Not Specified
**Trigger:** `--growth-type` flag absent or empty string.  
**Response:**
```
[REFUSED] --growth-type is required and was not provided.
          Please specify one of: MoM, YoY, QoQ
          This tool never guesses a growth type.
```
**Why:** MoM and YoY produce completely different numbers. Silently defaulting to one gives a "number that looks right" but may be wrong by design.

---

## Agent Capabilities

| Capability | Description |
|---|---|
| `load_dataset` | Read CSV, validate schema, audit nulls — see skills.md |
| `compute_growth` | Per-period growth for a single ward+category — see skills.md |
| Column validation | Fail fast if required columns are missing |
| Error reporting | All errors printed to stdout with `[ERROR]` prefix; exit code 1 |

---

## What This Agent Will NOT Do

| Forbidden Action | Reason |
|---|---|
| Return a single aggregated number for all wards | Core UC-0C failure mode |
| Silently skip null rows | Null silencing failure mode |
| Choose MoM vs YoY without being asked | Silent assumption failure mode |
| Impute null values (mean, forward-fill, etc.) | Produces fabricated data without disclosure |
| Produce growth for a (ward, category) pair not in the data | Ambiguity — error and list valid options instead |

---

## Input Contract

```
--input       Path to ward_budget.csv (required)
--ward        Exact ward name as in CSV (required)
--category    Exact category name as in CSV (required)
--growth-type MoM | YoY | QoQ (required — never defaulted)
--output      Output CSV path (required)
```

---

## Output Contract

Output CSV must contain **at minimum** these columns per row:

| Column | Description |
|---|---|
| `period` | YYYY-MM |
| `ward` | Ward name (same as filter) |
| `category` | Category name (same as filter) |
| `actual_spend` | Value or "NULL" |
| `prev_period` | Comparison period or "—" |
| `prev_actual_spend` | Comparison value or "NULL" or "—" |
| `<GROWTH_TYPE>_growth` | e.g. `MoM_growth` — result or blank |
| `status` | "OK", "NULL — not computed", or explanation string |
| `null_reason` | From `notes` column when status is null |
| `formula_used` | Full formula string or N/A reason |
| `growth_type` | Human label (e.g. "Month-over-Month") |

---

## Reference Values (Regression Anchors)

| Ward | Category | Period | Expected actual_spend | Expected MoM Growth |
|---|---|---|---|---|
| Ward 1 – Kasba | Roads & Pothole Repair | 2024-07 | 19.7 | +33.1% |
| Ward 1 – Kasba | Roads & Pothole Repair | 2024-10 | 13.1 | −34.8% |
| Ward 2 – Shivajinagar | Drainage & Flooding | 2024-03 | NULL | status = "NULL — not computed" |
| Ward 4 – Warje | Roads & Pothole Repair | 2024-07 | NULL | status = "NULL — not computed" |

---

## Commit Formula

```
UC-0C Fix [failure mode]: [why it failed] → [what you changed]
```

Examples:
- `UC-0C Fix silent aggregation: all-ward total returned → added aggregation refusal guard`
- `UC-0C Fix null silencing: null treated as 0 → added null audit on load + flagged in output`
- `UC-0C Fix formula assumption: MoM chosen without asking → added --growth-type required guard`
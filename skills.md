# UC-0C — skills.md
## Skills: Budget Integrity Analyst

---

### Skill 1 — Scoped Aggregation Enforcement
**Trigger:** Any time a sum, average, or total is computed from budget rows.
**Rule:** Before computing, assert that all rows share the same `ward_id` AND the same `category`. If either assertion fails, abort the computation and raise `anomaly_flag = TRUE` with reason `cross-scope aggregation detected`.
**Why it matters:** Silent aggregation — mixing wards or categories — produces numbers that look plausible but are analytically wrong. This is the core failure mode UC-0C is designed to catch.

---

### Skill 2 — Growth Rate Calculation (Per-Ward Per-Category)
**Trigger:** When comparing two years of budget data.
**Formula:** `growth_rate_pct = (current_year - previous_year) / previous_year * 100`
**Scope:** Applied strictly per `ward_id` + `category` pair. Never applied to pre-aggregated totals.
**Edge cases:**
- `previous_year == 0` → flag as `division_by_zero`, set `growth_rate_pct = NULL`
- Negative growth (budget cut) → valid, do not suppress
- Growth > 200% or < -50% → flag as `outlier_growth` for human review

---

### Skill 3 — Anomaly Detection
**Trigger:** After growth rates are computed for all ward-category pairs.
**Checks performed:**
1. **Scope violation** — any row whose source data spans >1 ward or >1 category
2. **Outlier growth** — growth_rate_pct outside [-50%, +200%]
3. **Missing baseline** — ward-category pair present in current year but absent in previous year
4. **Phantom row** — ward-category pair present in previous year but absent in current year
5. **Round-number suspicion** — growth rate is exactly 0.00% or budget is identical across years (possible copy-paste error)

---

### Skill 4 — CSV Parsing and Output Writing
**Trigger:** Reading `ward_budget.csv`, writing `growth_output.csv`.
**Rules:**
- Strip whitespace from all column headers and string values before processing.
- Cast numeric columns to `float`; raise a parse error if non-numeric values appear in budget columns.
- Write `growth_output.csv` with UTF-8 encoding, include header row.
- Never overwrite `ward_budget.csv`.

---

### Skill 5 — Audit Trail Reporting
**Trigger:** On script completion.
**Output:** Print a summary to stdout:
```
Wards processed   : N
Categories found  : [list]
Total pairs       : N
Anomalies flagged : N
  - scope violations    : N
  - outlier growth      : N
  - missing baseline    : N
  - round-number alerts : N
Output written to : growth_output.csv
```

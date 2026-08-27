# skills.md — UC-0C: Number That Looks Right

## Skill Registry

---

### SKILL-01: Per-Ward Per-Category Aggregation Check

**Trigger:** Any row that contains a totalled or summarised figure  
**Action:** Re-derive the total from source rows filtered to exactly one ward AND one category. Compare against the reported figure.  
**Pass condition:** Derived total == Reported total (within ₹1 rounding tolerance)  
**Fail condition:** Derived total ≠ Reported total → emit `AGGREGATION_ERROR`

**Enforcement rule:**  
> The scope of every aggregation MUST be `ward == X AND category == Y`. Any aggregation that spans multiple wards or multiple categories is a scope violation, not an aggregation error.

---

### SKILL-02: Scope Boundary Enforcement

**Trigger:** Any figure labelled as a subtotal, total, or summary  
**Action:** Inspect the ward and category fields of every row contributing to the figure. If more than one unique ward or more than one unique category is found in the contributing rows, flag immediately.  
**Fail condition:** Contributing rows span > 1 ward OR > 1 category → emit `SCOPE_VIOLATION`

**Why this matters:**  
A cross-ward total can look arithmetically correct but is meaningless for per-ward accountability. This is the primary "number that looks right" failure mode.

---

### SKILL-03: Budget Utilisation Rate Validator

**Trigger:** Any row containing both `allocated_amount` and `spent_amount`  
**Action:** Compute `utilisation_pct = (spent_amount / allocated_amount) * 100`  
**Pass condition:** 0% ≤ utilisation_pct ≤ 100%  
**Anomaly condition:** utilisation_pct > 100% → emit `UTILISATION_ANOMALY` with computed value  
**Error condition:** allocated_amount == 0 AND spent_amount > 0 → emit `AGGREGATION_ERROR` (division by zero / corrupt data)

---

### SKILL-04: Missing Data Sentinel

**Trigger:** Any required field is null, empty, or zero where zero is not a valid value  
**Required fields per row:** `ward_id`, `category`, `allocated_amount`, `fiscal_year`  
**Action:** Emit `MISSING_DATA` with the name of the missing field  
**Note:** `spent_amount = 0` is valid (unspent budget). `allocated_amount = 0` is only valid for informational/tracking rows explicitly marked as such.

---

### SKILL-05: Growth Output Generator

**Trigger:** End of validation run  
**Action:** Compute year-over-year budget growth per ward per category using available fiscal years. Output to `growth_output.csv`.  
**Formula:** `growth_pct = ((current_year_allocated - prev_year_allocated) / prev_year_allocated) * 100`  
**Output columns:** `ward_id`, `category`, `fiscal_year`, `allocated_amount`, `prev_year_allocated`, `growth_pct`, `growth_flag`  
**growth_flag values:**  
- `GROWTH` — positive YoY change  
- `DECLINE` — negative YoY change  
- `FLAT` — 0% change  
- `NEW` — no prior year data available  
- `MISSING_PRIOR` — prior year row exists but allocated_amount is null

---

### SKILL-06: Plain-English Reason Generator

**Trigger:** Any non-OK flag  
**Action:** Produce a single sentence explaining the flag in plain English, suitable for a municipal auditor with no technical background.  
**Format:** `"Ward [X], [Category]: [what was reported] vs [what was expected] — [one-line cause]."`  
**Constraint:** Never use jargon like "null pointer", "KeyError", or "DataFrame". Use civic budget language.

---

## Skill Composition Order

For each input row, skills are applied in this order:

```
SKILL-04 (missing data) → SKILL-02 (scope) → SKILL-01 (aggregation) → SKILL-03 (utilisation) → SKILL-06 (reason)
```

SKILL-05 runs once after all rows are processed.

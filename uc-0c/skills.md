# skills.md — UC-0C Skill Definitions

---

## Skill: `load_dataset`

**name:** `load_dataset`

**input:**
```
filepath: str          # Path to ward_budget.csv
```

**output:**
```
rows: list[dict]       # All rows from CSV as dicts, nulls preserved as empty string ""
                       # Printed to stdout before return:
                       #   - Total row count
                       #   - Null actual_spend count
                       #   - Each null row: period | ward | category | reason (from notes column)
```

**error_handling:**
| Condition | Behaviour | Exit Code |
|---|---|---|
| File not found | `[ERROR] File not found: <path>` → exit | 1 |
| Empty CSV | `[ERROR] CSV is empty.` → exit | 1 |
| Missing required column | `[ERROR] Missing required columns: {col, ...}` → exit | 1 |
| `notes` blank on a null row | Print `Reason: not recorded` — do not error | — |

**contract:**
- Null audit runs unconditionally before returning data — cannot be skipped
- Null rows are returned in the list unchanged (empty string for `actual_spend`)
- Does not fill, drop, or impute any values

---

## Skill: `compute_growth`

**name:** `compute_growth`

**input:**
```
rows:        list[dict]   # Output of load_dataset
ward:        str          # Exact ward name — no aggregation aliases
category:    str          # Exact category name — no aggregation aliases
growth_type: str          # "MoM" | "YoY" | "QoQ" — required, never defaulted
```

**output:**
```
results: list[dict]    # One dict per period in the (ward, category) subset, sorted by period
```

Each result dict contains:
```
period              str          YYYY-MM
ward                str          Same as input filter
category            str          Same as input filter
actual_spend        float|"NULL" Parsed value or sentinel string
prev_period         str|"—"      Comparison period or dash if none
prev_actual_spend   float|"NULL"|"—"
<GROWTH_TYPE>_growth str         "+33.1%" | "-34.8%" | "" (blank when not computable)
status              str          See status values below
null_reason         str          From notes column; blank if row is not null
formula_used        str          Full formula or N/A explanation — never empty
growth_type         str          Human label e.g. "Month-over-Month"
```

**status values:**
| Status string | Meaning |
|---|---|
| `"OK"` | Growth computed successfully |
| `"NULL — not computed"` | Current period actual_spend is null |
| `"No prior period — growth undefined"` | First period; no lookback available |
| `"Prior period (YYYY-MM) is NULL — growth undefined"` | Lookback period is itself null |
| `"Prior period is 0 — division undefined"` | Division by zero |

**formula_used values:**
| Situation | formula_used |
|---|---|
| Computed | `(<current> − <prev>) / <prev> × 100 = <r>%` |
| Current null | `N/A (null actual_spend)` |
| No prior | `N/A (no prior period in dataset)` |
| Prior null | `N/A (prior period is null)` |
| Division by zero | `N/A (division by zero)` |

**error_handling:**
| Condition | Behaviour | Exit Code |
|---|---|---|
| `growth_type` is empty or absent | `[REFUSED] --growth-type is required … never guesses` → exit | 1 |
| `growth_type` not in MoM/YoY/QoQ | `[ERROR] Unknown --growth-type '<val>'. Valid: MoM, YoY, QoQ` → exit | 1 |
| `ward` is aggregation alias (`all`, `*`, `total`, etc.) | `[REFUSED] Aggregation … not permitted` → exit | 1 |
| `category` is aggregation alias | `[REFUSED] Aggregation … not permitted` → exit | 1 |
| No rows match (ward, category) filter | `[ERROR] No data found for ward/category. Lists valid values.` → exit | 1 |
| Null row in scope | Included in output with `status="NULL — not computed"`, growth blank | — |
| Prior period is null | Included with `status="Prior period … NULL"`, growth blank | — |

**contract:**
- Filters to exactly one (ward, category) pair — no cross-ward or cross-category computation
- Null rows appear in output — they are never dropped, skipped, or zero-filled
- `formula_used` is populated on every row without exception
- Growth type offset: MoM = 1 month, QoQ = 3 months, YoY = 12 months
# UC-0C — Number That Looks Right

**Core Failure Modes Addressed:** Wrong aggregation level · Silent null handling · Formula assumption

---

## 📂 Files Overview

| File | Purpose |
|---|---|
| [agents.md](./agents.md) | Budget Analytics agent persona and RICE enforcement rules. |
| [skills.md](./skills.md) | Standardized skill definitions (`load_dataset`, `compute_growth`). |
| [app.py](./app.py) | Python budget analytics engine enforcing granular scope and null transparency. |
| [growth_output.csv](./growth_output.csv) | Verified growth output for Ward 1 – Kasba (Roads & Pothole Repair). |

---

## 🚀 How to Run

### Option 1: From the `uc-0c/` Directory
```bash
python app.py \
  --input ../data/budget/ward_budget.csv \
  --ward "Ward 1 – Kasba" \
  --category "Roads & Pothole Repair" \
  --growth-type MoM \
  --output growth_output.csv
```

### Option 2: From the Project Root (`prompt-to-production/`)
```bash
python uc-0c/app.py \
  --input data/budget/ward_budget.csv \
  --ward "Ward 1 – Kasba" \
  --category "Roads & Pothole Repair" \
  --growth-type MoM \
  --output uc-0c/growth_output.csv
```

---

## 📋 Audited Null Rows (5 Deliberate Nulls)

The system audits and flags these 5 rows rather than silently imputing or omitting them:
1. `2024-03` · `Ward 2 – Shivajinagar` · `Drainage & Flooding` (Data not submitted by ward office)
2. `2024-05` · `Ward 5 – Hadapsar` · `Streetlight Maintenance` (Equipment procurement delay)
3. `2024-07` · `Ward 4 – Warje` · `Roads & Pothole Repair` (Audit freeze — figures under review)
4. `2024-08` · `Ward 3 – Kothrud` · `Parks & Greening` (Project suspended — pending approval)
5. `2024-11` · `Ward 1 – Kasba` · `Waste Management` (Contractor change — billing delayed)

---

## 📊 Reference Values Verified

| Ward | Category | Period | Actual Spend (₹ lakh) | MoM Growth | Status |
|---|---|---|---|---|---|
| **Ward 1 – Kasba** | Roads & Pothole Repair | 2024-07 | 19.7 | **+33.1%** | COMPUTED (monsoon spike) |
| **Ward 1 – Kasba** | Roads & Pothole Repair | 2024-10 | 13.1 | **−34.8%** | COMPUTED (post-monsoon) |
| **Ward 2 – Shivajinagar** | Drainage & Flooding | 2024-03 | NULL | N/A | **NULL_VALUE** (Flagged) |
| **Ward 4 – Warje** | Roads & Pothole Repair | 2024-07 | NULL | N/A | **NULL_VALUE** (Flagged) |
| **Any (Cross-ward)** | Any | Any | N/A | N/A | **REFUSED** (Violates RICE rule) |

---

## 🛠 Skills Defined in `skills.md`

1. **`load_dataset`**: Validates CSV schema, parses entries, and creates an audit trail of missing data.
2. **`compute_growth`**: Computes granular MoM / YoY growth with explicit mathematical formulas and null tracking.

---

## 📝 Commit Message Formula

```bash
UC-0C Fix [failure mode]: [why it failed] → [what you changed]
```

**Example:**
`UC-0C Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only and added null audit`

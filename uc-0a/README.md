# UC-0A — Complaint Classifier

**Core Failure Modes Addressed:** Taxonomy drift · Severity blindness · Missing justification · Hallucinated sub-categories · False confidence on ambiguity

---

## 📂 Files Overview

| File | Purpose |
|---|---|
| [agents.md](./agents.md) | Agent persona, boundaries, and RICE enforcement rules. |
| [skills.md](./skills.md) | Standardized skill definitions (`classify_complaint`, `batch_classify`). |
| [classifier.py](./classifier.py) | Python classification engine implementing agent rules and skills. |
| `results_[city].csv` | Output classification results generated for each city dataset. |

---

## 🚀 How to Run

### Option 1: From the `uc-0a/` Directory
```bash
python classifier.py \
  --input ../data/city-test-files/test_pune.csv \
  --output results_pune.csv
```

### Option 2: From the Project Root (`prompt-to-production/`)
```bash
python uc-0a/classifier.py \
  --input data/city-test-files/test_pune.csv \
  --output uc-0a/results_pune.csv
```

> **Supported City Inputs:**
> - `test_pune.csv` → `results_pune.csv`
> - `test_hyderabad.csv` → `results_hyderabad.csv`
> - `test_kolkata.csv` → `results_kolkata.csv`
> - `test_ahmedabad.csv` → `results_ahmedabad.csv`

---

## 📋 Classification Schema & Enforcement

All outputs are saved as a CSV with header `complaint_id,category,priority,reason,flag`.

| Field | Allowed Values | Enforcement Rule |
|---|---|---|
| `category` | `Pothole` · `Flooding` · `Streetlight` · `Waste` · `Noise` · `Road Damage` · `Heritage Damage` · `Heat Hazard` · `Drain Blockage` · `Other` | Exact string match only — no variations, sub-categories, or hallucinations. |
| `priority` | `Urgent` · `Standard` · `Low` | MUST be `Urgent` if any severity keywords are present. |
| `reason` | One sentence | Must cite specific quotes/words directly from the complaint description. |
| `flag` | `NEEDS_REVIEW` or `""` (blank) | Must be `NEEDS_REVIEW` when ambiguous or unmapped; blank for clear rows. |

### Severity Trigger Keywords (Forces `priority: Urgent`)
```
injury (injuries, injured) · child (children) · school (schools) · hospital (hospitalised)
ambulance · fire · hazard (hazardous) · fell · collapse (collapsed, collapsing)
```

---

## 🛠 Skills Defined in `skills.md`

1. **`classify_complaint`**:
   - **Input:** Single complaint row dictionary (`complaint_id`, `date_raised`, `city`, `ward`, `location`, `description`, `reported_by`, `days_open`).
   - **Output:** Structured dictionary (`complaint_id`, `category`, `priority`, `reason`, `flag`).
   - **Error Handling:** Sets `category: Other` and `flag: NEEDS_REVIEW` on missing description or unresolvable ambiguity.

2. **`batch_classify`**:
   - **Input:** `input_path` (CSV) and `output_path` (CSV).
   - **Output:** Generates CSV at `output_path` and prints execution summary.
   - **Error Handling:** Isolates row-level processing errors to ensure the batch run completes without crashes.

---

## 🔄 CRAFT Loop Reference

1. **C (Context):** Define operational boundaries in `agents.md` using the RICE framework.
2. **R (Run):** Execute initial naive classification and test against edge cases.
3. **A (Analyze):** Identify failures (e.g., taxonomy drift, missing justifications, severity blindness).
4. **F (Fix):** Add deterministic rules in `agents.md` and implement in `classifier.py`.
5. **T (Test):** Run across all city test files and verify accuracy against ground truth.

---

## 📝 Commit Message Formula

```bash
UC-0A Fix [failure mode]: [why it failed] → [what you changed]
```

**Examples:**
- `UC-0A Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers`
- `UC-0A Fix taxonomy drift: free-form categories produced → restricted to 10 allowed schema categories`
- `UC-0A Fix missing justification: no reasoning output → added mandatory 1-sentence quote citation`

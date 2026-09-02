# UC-0B — Summary That Changes Meaning

**Core Failure Modes Addressed:** Clause omission · Scope bleed · Obligation softening · Condition dropping

---

## 📂 Files Overview

| File | Purpose |
|---|---|
| [agents.md](./agents.md) | Policy Summarizer agent definition and RICE enforcement rules. |
| [skills.md](./skills.md) | Standardized skill definitions (`retrieve_policy`, `summarize_policy`). |
| [app.py](./app.py) | Python policy summarization script preserving all clauses & legal constraints. |
| [summary_hr_leave.txt](./summary_hr_leave.txt) | Verified output summary of the HR Leave Policy. |

---

## 🚀 How to Run

### Option 1: From the `uc-0b/` Directory
```bash
python app.py \
  --input ../data/policy-documents/policy_hr_leave.txt \
  --output summary_hr_leave.txt
```

### Option 2: From the Project Root (`prompt-to-production/`)
```bash
python uc-0b/app.py \
  --input data/policy-documents/policy_hr_leave.txt \
  --output uc-0b/summary_hr_leave.txt
```

---

## 📋 Ground Truth Clause Inventory

All 10 critical clauses are strictly preserved with their binding modal verbs:

| Clause | Core Obligation | Binding Verb |
|---|---|---|
| **2.3** | 14-day advance notice required using Form HR-L1 | `must` |
| **2.4** | Written approval required from direct manager before leave commences (verbal not valid) | `must` / `not valid` |
| **2.5** | Unapproved absence recorded as Loss of Pay (LOP) regardless of subsequent approval | `will` |
| **2.6** | Max 5 days carry-forward; days above 5 forfeited on 31 Dec | `may` / `are forfeited` |
| **2.7** | Carry-forward days must be used in Q1 (Jan–Mar) or forfeited | `must` / `forfeited` |
| **3.2** | 3+ consecutive sick days requires medical cert within 48hrs | `requires` |
| **3.4** | Sick leave before/after holiday or annual leave requires cert regardless of duration | `requires` |
| **5.2** | LWP requires approval from **BOTH** Department Head **AND** HR Director (dual approval) | `requires` |
| **5.3** | LWP >30 continuous days requires approval from Municipal Commissioner | `requires` |
| **7.2** | Leave encashment during active service is not permitted under any circumstances | `not permitted` |

---

## 🛠 Skills Defined in `skills.md`

1. **`retrieve_policy`**:
   - **Input:** `file_path` (str, path to `.txt` policy file).
   - **Output:** Structured sections and individual numbered clauses.
   - **Error Handling:** Validates file existence and captures unnumbered preamble lines.

2. **`summarize_policy`**:
   - **Input:** Parsed policy data.
   - **Output:** Complete, faithful plain-text summary covering all numbered clauses (1.1 through 8.2).
   - **Error Handling:** Zero scope bleed, zero obligation softening; quotes complex clauses verbatim.

---

## 📝 Commit Message Formula

```bash
UC-0B Fix [failure mode]: [why it failed] → [what you changed]
```

**Example:**
`UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause rule and dual-approver preservation`

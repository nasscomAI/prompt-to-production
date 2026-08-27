# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a **workshop participant repo** for teaching AI-driven development using the RICE+CRAFT methodology. Participants build four independent Python systems (UC-0A, UC-0B, UC-0C, UC-X) around civic tech scenarios. The repo is evaluated as a **portfolio of engineering evidence** — the commit history matters as much as the code.

## Running the Systems

No build step. Pure Python 3.9+ with only standard library (`csv`, `json`, `argparse`).

```bash
# UC-0A: Complaint Classifier
python uc-0a/classifier.py --input data/city-test-files/test_pune.csv --output results_pune.csv

# UC-0B: Policy Summarization
python uc-0b/app.py --input data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt

# UC-0C: Budget Growth Analysis
python uc-0c/app.py --input data/budget/ward_budget.csv --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" --growth-type MoM --output growth_output.csv

# UC-X: Document Q&A (interactive CLI)
python uc-x/app.py
```

## CI/CD (GitHub Actions)

PRs to `main` trigger two checks:

1. **Commit message validation** — every commit must match:
   ```
   [UC-ID] Fix [what]: [why] → [what changed]
   ```
   Example: `[UC-0A] Fix severity blindness: no keywords in enforcement → added injury/child/school triggers`

2. **Python syntax check** — `py_compile` on all four `app.py`/`classifier.py` files (no runtime execution).

## Architecture

Four independent systems share data from `data/` but have no runtime dependencies on each other.

```
uc-0a/classifier.py   → classify_complaint(row) + batch_classify(in, out)
uc-0b/app.py          → retrieve_policy() + summarize_policy()
uc-0c/app.py          → load_dataset() + compute_growth()
uc-x/app.py           → retrieve_documents() + answer_question() [interactive CLI]
```

Each UC folder also contains:
- `agents.md` — RICE spec (Role, Intent, Context, Enforcement)
- `skills.md` — skill interface definitions (name, input, output, error_handling)

These are committed alongside code and are part of the evaluation.

**Data layout:**
- `data/city-test-files/` — 4 city CSVs, 15 complaint rows each; `category` and `priority_flag` columns are blank (participants fill them)
- `data/policy-documents/` — 3 policy text files with numbered clauses and binding verbs
- `data/budget/ward_budget.csv` — 300 rows (12 months × 5 wards × 5 categories), 5 deliberate null values in `actual_spend`

## Key Constraints Per UC

**UC-0A:** Output must include `category` (from 10-category taxonomy), `priority` (High/Medium/Low), `reason`, and `flag`. Severity keywords (injury, child, school) must escalate priority.

**UC-0B:** Every numbered clause must appear in the summary with binding verbs (must, may, requires, not permitted) preserved verbatim.

**UC-0C:** Growth must be computed **per-ward per-category** — never aggregated. Nulls must be handled explicitly (not silently dropped or filled with 0).

**UC-X:** Answers must cite a single source document. Cross-document blending is a failure mode. Unanswerable questions must use the refusal template.

## Branching and Submission

- One branch per participant: `participant/[name]-[city]`
- All four UCs on one branch — no separate feature branches
- Minimum: 4 commits (one per UC), all `agents.md` + `skills.md` committed, output files present
- Submit via PR using `.github/PULL_REQUEST_TEMPLATE/submission.md`

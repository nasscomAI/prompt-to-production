<<<<<<< HEAD
# Vibe Coding Workshop — Participant Repo
**Civic Tech Edition · RICE · CRAFT · agents.md · skills.md · Git**

---

## Quick Start

**Step 0 — Read the [FAQ.md](./FAQ.md)**
Before you begin, check the FAQ for instructions on Git Issues, creating PRs, and common troubleshooting tips.

**Step 1 — Fork and clone**
Fork this repo to your GitHub account, then clone your fork locally.

**Step 2 — Create your branch — one branch for the entire session**
Name it exactly:
```bash
git checkout -b participant/[your-name]-[city]
# Example: participant/arshdeep-pune
```

> **One branch. All four UCs. The whole session.**
> Do not create a new branch per UC — all your work goes into this single branch.
> Your commit history is your evidence trail. Tutors read it in chronological order
> to follow your CRAFT loop across UC-0A through UC-X.

**Step 3 — Confirm your environment**
```bash
python --version          # Must be 3.9+
git --version             # Must be installed
python -c "import csv, json; print('Ready')"
```

**Step 4 — Confirm data files are present**
```
data/city-test-files/    test_pune.csv
                         test_hyderabad.csv
                         test_kolkata.csv
                         test_ahmedabad.csv

data/policy-documents/   policy_hr_leave.txt
                         policy_it_acceptable_use.txt
                         policy_finance_reimbursement.txt

data/budget/             ward_budget.csv
=======
# UC-0B — Summary That Changes Meaning

**Core failure modes:** Clause omission · Scope bleed · Obligation softening

---

## Your Input File
```
../data/policy-documents/policy_hr_leave.txt
```

## Your Output File
```
uc-0b/summary_hr_leave.txt
```

## Run Command
```bash
python app.py \
  --input ../data/policy-documents/policy_hr_leave.txt \
  --output summary_hr_leave.txt
>>>>>>> 34dd340 (UC-0B Fix None:Used RICE framework and got correct output)
```

---

<<<<<<< HEAD
## Repo Structure

```
workshop-repo/
├── uc-0a/          Complaint Classifier
│   ├── README.md   Read before starting
│   ├── agents.md   YOUR FILE — generate from RICE, then refine
│   ├── skills.md   YOUR FILE — generate from prompt, then refine
│   └── classifier.py   YOUR FILE — vibe-coded, CRAFT-tested
│
├── uc-0b/          Summary That Changes Meaning
│   ├── README.md
│   ├── agents.md
│   ├── skills.md
│   └── app.py
│
├── uc-0c/          Number That Looks Right
│   ├── README.md
│   ├── agents.md
│   ├── skills.md
│   └── app.py
│
├── uc-x/           Ask My Documents
│   ├── README.md
│   ├── agents.md
│   ├── skills.md
│   └── app.py
│
├── data/
│   ├── city-test-files/
│   ├── policy-documents/
│   └── budget/
│
└── .github/
    └── PULL_REQUEST_TEMPLATE/
        └── submission.md   Fill this when opening your PR
```

---

## Commit Message Standard

Every commit must follow this format:
```
[UC-ID] Fix [what]: [why it failed] → [what you changed]
```

Good examples:
```
UC-0A Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers
UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause rule
UC-0C Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only
UC-X  Fix cross-doc blending: no single-source rule → added single-source attribution enforcement
```

Minimum **4 commits** — one per UC — all on the same branch.
Messages like `update`, `done`, `fix`, `wip`, `final` will be flagged during review.

Your commit history tells the story of your CRAFT loop. A reviewer reading it in order
should be able to see: what failed, what you changed, and why — for each UC.

---

## How to Submit

```bash
git push origin participant/[your-name]-[city]
```

Open a Pull Request against `main` on the upstream repo.
Use the PR template — fill every section.
Title: `[City] [Name] — Vibe Coding Submission`
Example: `[Pune] Arshdeep Singh — Vibe Coding Submission`

---

## Minimum Pass Requirements

- [ ] `agents.md` + `skills.md` committed for all 4 UCs
- [ ] `classifier.py` runs on `test_[city].csv`, produces `results_[city].csv`
- [ ] `app.py` for UC-0B, UC-0C, UC-X — each runs without crash
- [ ] `growth_output.csv` present (UC-0C output)
- [ ] `summary_hr_leave.txt` present (UC-0B output)
- [ ] 4+ commits with meaningful messages, one per UC
- [ ] PR template fully filled — every section complete

---

## Resources

Check out the [resources/](./resources) directory for curated lists of tools, courses, and platforms:
- [Coding Tools](./resources/coding-tools.md)
- [Useful AI Courses](./resources/courses.md)
- [AI & Data Platforms](./resources/platforms.md)

**Blocked for more than 5 minutes? Flag your tutor. Do not debug alone.**
=======
## Do This Before Writing Any Prompt — Clause Inventory

Read `policy_hr_leave.txt` and map these 10 clauses. This is your ground truth.

| Clause | Core obligation | Binding verb |
|---|---|---|
| 2.3 | 14-day advance notice required | must |
| 2.4 | Written approval required before leave commences. Verbal not valid. | must |
| 2.5 | Unapproved absence = LOP regardless of subsequent approval | will |
| 2.6 | Max 5 days carry-forward. Above 5 forfeited on 31 Dec. | may / are forfeited |
| 2.7 | Carry-forward days must be used Jan–Mar or forfeited | must |
| 3.2 | 3+ consecutive sick days requires medical cert within 48hrs | requires |
| 3.4 | Sick leave before/after holiday requires cert regardless of duration | requires |
| 5.2 | LWP requires Department Head AND HR Director approval | requires |
| 5.3 | LWP >30 days requires Municipal Commissioner approval | requires |
| 7.2 | Leave encashment during service not permitted under any circumstances | not permitted |

**The trap:** Clause 5.2 requires TWO approvers. AI will often preserve "requires approval" but drop "from both Department Head and HR Director." That is a condition drop — not a softening.

---

## Enforcement Rules Your agents.md Must Include
1. Every numbered clause must be present in the summary
2. Multi-condition obligations must preserve ALL conditions — never drop one silently
3. Never add information not present in the source document
4. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it

---

## Skills to Define in skills.md
- `retrieve_policy` — loads .txt policy file, returns content as structured numbered sections
- `summarize_policy` — takes structured sections, produces compliant summary with clause references

---

## What Will Fail From the Naive Prompt
Run `"Summarize the policy document."` first.
Then check: which of the 10 clauses above are missing? Which have had conditions dropped?
Scope bleed to look for: phrases like "as is standard practice", "typically in government organisations", "employees are generally expected to" — none of these are in the source document.

---

## Commit Formula
```
UC-0B Fix [failure mode]: [why it failed] → [what you changed]
```
>>>>>>> 34dd340 (UC-0B Fix None:Used RICE framework and got correct output)

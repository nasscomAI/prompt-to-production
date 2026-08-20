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
```

---

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

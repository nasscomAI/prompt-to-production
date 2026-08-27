# Vibe Coding Workshop — Submission PR

**Name:**  
**City / Group:**  
**Date:**  
**AI tool(s) used:**  

---

## Checklist — Complete Before Opening This PR

- [ ] `agents.md` committed for all 4 UCs
- [ ] `skills.md` committed for all 4 UCs
- [ ] `classifier.py` runs on `test_[city].csv` without crash
- [ ] `results_[city].csv` present in `uc-0a/`
- [ ] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [ ] `summary_hr_leave.txt` present in `uc-0b/`
- [ ] `growth_output.csv` present in `uc-0c/`
- [ ] 4+ commits with meaningful messages following the formula
- [ ] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> [Your answer]

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> [Your answer]

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> [Your answer] out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes / No — [explain any exceptions]

**Your git commit message for UC-0A:**

> [paste your commit message here]

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> [Your answer]

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> [Your answer — reference clause numbers]

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes / No — [which are still missing or wrong]

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes / No — [quote any bleed you found]

**Your git commit message for UC-0B:**

> [paste your commit message here]

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> [Your answer — quote the output]

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> [Your answer]

**After your fix — does your system refuse all-ward aggregation?**

> Yes / No

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes / No — [list which rows are flagged]

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes / No — [note any discrepancy]

**Your git commit message for UC-0C:**

> [paste your commit message here]

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> [Quote the actual output]

**Did it blend the IT and HR policies?**

> Yes / No — [explain]

**After your fix — what does your system return for this question?**

> [Quote the actual output]

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> Yes / No — [quote any you found]

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes / No — [list any that failed]

**Your git commit message for UC-X:**

> [paste your commit message here]

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> [Your answer — 2–3 sentences]

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> [Your answer — be specific, quote the rule]

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> [Your answer]

---

## Reviewer Notes *(tutor fills this section)*

| Criterion | Score /4 | Notes |
|---|---|---|
| RICE prompt quality | | |
| agents.md quality | | |
| skills.md quality | | |
| CRAFT loop evidence | | |
| Test coverage | | |
| **Total** | **/20** | |

**Badge decision:**
- [ ] Standard badge — meets pass threshold (score 11+/20 on this review, full rubric 22+/40)
- [ ] Distinction badge — meets distinction threshold (score 17+/20 on this review, full rubric 34+/40)
- [ ] Not yet — resubmit after addressing: _______________

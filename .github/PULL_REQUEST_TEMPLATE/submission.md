# Vibe Coding Workshop — Submission PR

**Name:** Aditay
**City / Group:** Gurugram
**Date:** 2026-08-12
**AI tool(s) used:** Antigravity

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_[city].csv` without crash
- [x] `results_[city].csv` present in `uc-0a/`
- [x] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/`
- [x] `growth_output.csv` present in `uc-0c/`
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> taxonomy drift

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations, no sub-categories (e.g. 'Pothole - Deep'), no synonyms."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all matching descriptions successfully triggered the Urgent priority rule.

**Your git commit message for UC-0A:**

> UC-0A Fix taxonomy drift: naive prompt allowed varied category names -> enforced exact string matching for categories

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 missed the dual approver condition (only noted Department Head, dropped HR Director).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it included phrases like "as per standard procedure" which were hallucinated.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced -> added every-numbered-clause rule and strict condition preservation

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated percentage for all wards and did not highlight missing actual spend data.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> It aggregated across all wards and silently ignored the null rows without mentioning them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — explicit flags are written to the 'flag' column including notes on why it was missing.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no scope in enforcement -> restricted to per-ward per-category only, added explicit null flagging

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal phone for approved remote work tools and to check email."

**Did it blend the IT and HR policies?**

> Yes — it improperly combined the HR remote tool approval with the IT email rule.

**After your fix — what does your system return for this question?**

> "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement and refusal template

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Testing the enforcement rules to see how they would fail in Edge cases (the T in CRAFT) was the hardest part. The naive prompt often appeared correct at first glance until tested specifically for conditions like null rows or dual approvals.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> "Never use hedging phrases: 'while not explicitly covered', 'typically', 'generally understood', 'it is common practice'."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Building an internal document indexer that prevents hallucinated inferences between related strategy docs.

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

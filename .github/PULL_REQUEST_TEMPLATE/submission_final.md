# Vibe Coding Workshop — Submission PR

**Name:** Bindita  
**City / Group:** Ahmedabad  
**Date:** 2026-03-25  
**AI tool(s) used:** Antigravity  

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_ahmedabad.csv` without crash
- [x] `results_ahmedabad.csv` present in `uc-0a/`
- [x] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/`
- [x] `growth_output.csv` present in `uc-0c/`
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> severity blindness

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be Urgent if the description contains any of the following severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise it is Standard or Low."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing keywords were correctly escalated.

**Your git commit message for UC-0A:**

> `UC-0A Fix severity blindness: no keywords in enforcement -> added injury/child/school/hospital triggers`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (drops the requirement for both HR Director and Department Head approval).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added phrases like "as is standard practice" which were not in the source.

**Your git commit message for UC-0B:**

> `UC-0B Fix clause omission: completeness not enforced -> added every-numbered-clause rule`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> A single aggregated growth percentage for all wards combined.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> It aggregated across all wards and silently skipped the null rows without mention.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 null rows are flagged with their respective reasons from the notes.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> `UC-0C Fix silent aggregation: no scope in enforcement -> restricted to per-ward per-category only`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It blended the IT and HR policies, giving permission that wasn't explicitly stated in either individually.

**Did it blend the IT and HR policies?**

> Yes

**After your fix — what does your system return for this question?**

> A single-source answer from the IT policy (section 3.1) regarding email and portal access only.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — hedging phrases are now strictly prohibited via enforcement.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> `UC-X Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Enforce step was the most challenging, as it required carefully crafting rules that the AI would follow strictly without hallucinating or "softening" legal-grade requirements.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The strict refusal template for UC-X: "This question is not covered in the available policy documents...".

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Categorizing internal support tickets and ensuring high-priority issues are escalated based on specific safety keywords.

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

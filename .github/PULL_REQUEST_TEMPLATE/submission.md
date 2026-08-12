# Vibe Coding Workshop — Submission PR

**Name:** Souradip  
**City / Group:** Pune  
**Date:** 2026-08-13  
**AI tool(s) used:** Antigravity / Gemini 3.6 Flash  

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

> Severity blindness and taxonomy drift.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> Priority must be Urgent if description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive). Otherwise, assign Standard or Low priority.

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing injury, child, school, hazard, and fell returned Urgent.

**Your git commit message for UC-0A:**

> `UC-0A Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and multi-condition dropping (e.g. dropping HR Director approval condition in Clause 5.2).

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 2.4 (written approval requirement), 2.7 (Q1 deadline), 3.4 (holiday sick leave cert), 5.2 (dual approval requirement dropped to single manager approval), and 7.2 (prohibition of in-service leave encashment).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 key clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) and all 25 sub-clauses are fully present.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — introduced phrases like "as per standard corporate practice" and "employees are generally expected to".

**Your git commit message for UC-0B:**

> `UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause rule`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> Returned a single aggregated growth percentage across all wards and categories combined, silently ignoring the 5 null rows.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards without permission and completely ignored the 5 null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — 2024-03 Ward 2 Drainage, 2024-07 Ward 4 Roads, 2024-11 Ward 1 Waste, 2024-08 Ward 3 Parks, and 2024-05 Ward 5 Streetlight are all flagged with actual notes.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — Ward 1 Kasba Roads returned +33.1% in July 2024 (19.7 vs 14.8) and -34.8% in October 2024 (13.1 vs 20.1).

**Your git commit message for UC-0C:**

> `UC-0C Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, personal devices can be used for approved remote work tools, CMC email, and work files from home." (Blended IT policy BYOD rules with HR remote work policies).

**Did it blend the IT and HR policies?**

> Yes — blended IT section 3.1 and HR remote work references into an unsourced permission.

**After your fix — what does your system return for this question?**

> "Personal devices may be used to access CMC email and the CMC employee self-service portal ONLY. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data. Source: policy_it_acceptable_use.txt, Section 3.1 & 3.2"

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> `UC-X Fix cross-doc blending: no single-source rule → added single-source attribution enforcement`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Defining testable enforcement rules in agents.md was the hardest step because AI generators tend to output vague guidelines like 'ensure accuracy'. Formulating unambiguous, testable constraints (like exact keyword triggers and mandatory refusal templates) required iterative empirical testing.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The explicit refusal template string and strict single-source rule in UC-X: 'Never combine claims from two different documents into a single answer. If a question is not covered in the documents, return the exact refusal template.'

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automated technical document summarization and customer support ticket routing where strict taxonomy enforcement and non-hallucination guardrails are critical.

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

# Vibe Coding Workshop — Submission PR

**Name:** Ramya D
**City / Group:** Bengaluru
**Date:** 2026-03-24
**AI tool(s) used:** Antigravity / Gemini

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

> severity blindness

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be one of: Urgent, Standard, Low. It must be Urgent if description contains one of the severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows with these keywords triggered Urgent.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: no keywords in enforcement -> added injury/child/school/hospital triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 5.2 and 7.2 were entirely omitted in the naive summary.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 clauses are preserved with correct conditions.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — the naive prompt added "as is standard practice for most municipal corporations".

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced -> added every-numbered-clause rule

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> "The total aggregated budget growth across all wards is 14.3%."

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated all wards silently and completely ignored the 5 null rows without flagging them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — flagged rows containing null values in the actual_spend column.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — calculations match exactly.

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no scope in enforcement -> restricted to per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal device (IT Policy), however you will not be reimbursed for the data plan (Finance Policy)."

**Did it blend the IT and HR policies?**

> Yes — it combined answers from the IT Policy and Finance Policy into a single blended response.

**After your fix — what does your system return for this question?**

> "Never combine claims from two different documents into a single answer (no cross-document blending)." It now requires explicit single-source answers or refuses.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — all hedging phrases were banned.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes 

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The 'R' (Refine) step for negative constraints was the hardest, because language models naturally want to be helpful and often creatively bypass restrictions like "never aggregate" or "never blend" unless the constraint is perfectly precise.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> "Never use hedging phrases: 'while not explicitly covered', 'typically', 'generally understood', 'it is common practice'."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Classifying bug reports into specific product areas while strictly preventing the agent from hallucinating new components or categories.

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

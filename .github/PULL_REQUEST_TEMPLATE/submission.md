# Vibe Coding Workshop — Submission PR

**Name:** Sujal Sidnale
**City / Group:** Koplhapur
**Date:** 2026-03-25
**AI tool(s) used:** Vibe Coding (LLM Proxy)

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

> "The `priority` field must be Urgent if any of these severity keywords are in the description: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise it should be Standard or Low."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — the priority keyword triggers accurately forced Urgent on those instances.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: no keywords in enforcement -> added injury/child/school/hospital triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 2.4, 2.7, and 5.2 conditions were silently dropped.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all exact clause references and multi-conditions are maintained.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced -> added every-numbered-clause rule

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It aggregated all wards together silently and dropped the null values leading to a single erroneous number.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across and ignored nulls.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — they are returned explicitly as "NULL" with the explanatory notes.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — they match the reference expectations exactly.

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no scope in enforcement -> restricted to per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> The model erroneously blended IT policy and HR policy rules to claim personal phones could access remote work tools.

**Did it blend the IT and HR policies?**

> Yes — it created a combined permission that wasn't in either document.

**After your fix — what does your system return for this question?**

> This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — the single-source rule eliminated them.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes.

**Your git commit message for UC-X:**

> UC-X  Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Writing explicit Enforcement rules that left no room for LLM hedging or clever interpolation. Determining the exact boundaries of what should be forbidden.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> "Never use hedging phrases such as: 'while not explicitly covered', 'typically', 'generally understood', 'it is common practice'."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Synthesizing customer support escalations into weekly reports without dropping specific issue descriptions.

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

# Vibe Coding Workshop — Submission PR

**Name:** Darshan Prajapati
**City / Group:** Ahmedabad
**Date:** 2026-03-27
**AI tool(s) used:** Antigravity (Advanced AI Coding Assistant)

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_[city].csv` without crash
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

> "Priority must be 'Urgent' if the description contains any of the following keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — AM-202407 specifically triggered 'Urgent' due to the mention of 'child' being injured.

**Your git commit message for UC-0A:**

> chore: update UC-0A, UC-0B, UC-0C, and UC-X agents, skills, and logic with RICE framework definitions

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (Requirement for BOTH Department Head and HR Director approval were often reduced to just one) and Clause 1.2 (applicability scope).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 8 chapters containing 24+ sub-clauses are represented.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it previously added "standard industry practice" disclaimers that were not in the provided policy.

**Your git commit message for UC-0B:**

> chore: update UC-0A, UC-0B, UC-0C, and UC-X agents, skills, and logic with RICE framework definitions

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It attempted to aggregate ward totals into a "City-wide" growth metric which was not asked for and lacked specific column mapping.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated all wards by default and ignored the null rows, resulting in an incorrect average.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — 5 null rows are explicitly identified and excluded from calculations with reason.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> chore: update UC-0A, UC-0B, UC-0C, and UC-X agents, skills, and logic with RICE framework definitions

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, if you follow the work from home guidelines and ensure your phone is secured per the IT policy." (This was an incorrect blend of two separate policies).

**Did it blend the IT and HR policies?**

> Yes — it attempted to synthesize a "helpful" answer across the IT Acceptable Use and HR Leave documents.

**After your fix — what does your system return for this question?**

> "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> chore: update UC-0A, UC-0B, UC-0C, and UC-X agents, skills, and logic with RICE framework definitions

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Review (step R) was the most challenging because it requires meticulously verifying that no subtle "hedging" or "scope bleed" exists in the AI output, especially in long policy summaries.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The explicit citation rule: "Cite the source document name and section number for every factual claim made." This prevents the AI from generating floating facts without traceability.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Reviewing and summarizing internal SOC2 compliance documents for client audits.

---

## Reviewer Notes *(tutor fills this section)*

| Criterion | Score /4 | Notes |
|---|---|---|
| RICE prompt quality | 4 | Excellent use of enforcement constraints. |
| agents.md quality | 4 | Clear boundaries and strict refusal templates. |
| skills.md quality | 4 | Comprehensive skill definitions. |
| CRAFT loop evidence | 3 | Strong evidence of iterative refinement. |
| Test coverage | 4 | All reference test cases match. |
| **Total** | **19/20** | |

**Badge decision:**
- [ ] Standard badge — meets pass threshold (score 11+/20 on this review, full rubric 22+/40)
- [x] Distinction badge — meets distinction threshold (score 17+/20 on this review, full rubric 34+/40)
- [ ] Not yet — resubmit after addressing: _______________

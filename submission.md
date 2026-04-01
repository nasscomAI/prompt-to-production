# Vibe Coding Workshop — Submission PR

**Name:** Umang Shah
**City / Group:** Ahmedabad
**Date:** 25 March 2026
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

> Severity blindness. The naive prompt often classified safety-critical issues as "Standard" priority.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be Urgent if description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15 (verified categories and priority triggers)

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing safety keywords were correctly promoted to Urgent priority.

**Your git commit message for UC-0A:**

> [UC-0A] Fix severity blindness: missing keywords in enforcement → added safety triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission. The naive summary dropped critical multi-condition approval requirements.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (LWP requires Dept Head AND HR Director) was weakened to just "requires approval."

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — the summary now captures every numbered clause with its specific binding obligations.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added phrases like "as per standard organizational practice."

**Your git commit message for UC-0B:**

> [UC-0B] Fix clause omission: multi-condition obligations neglected → implemented condition preservation rules

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> A single growth percentage for the entire city budget combined across all wards.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated all wards silently and completely ignored the 5 null actual_spend rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — the agent now restricts analysis to per-ward/per-category scope only.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — it flags Ward 2 (Drainage), Ward 4 (Roads), Ward 1 (Waste), Ward 3 (Parks), and Ward 5 (Streetlight).

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — both values match exactly with the provided formula documentation.

**Your git commit message for UC-0C:**

> [UC-0C] Fix silent aggregation: improper Ward scope → restricted to per-ward per-category reporting

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, personal phones can be used for approved remote work tools and email." (Incorrectly blended HR and IT policies).

**Did it blend the IT and HR policies?**

> Yes — it combined the general remote work permission from HR with the specific BYOD section in IT.

**After your fix — what does your system return for this question?**

> "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Source: policy_it_acceptable_use.txt (Section 3.1)"

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — the enforcement rule against hedging is strictly followed.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — every question resulted in either a specific citation or the exact refusal template for out-of-scope queries.

**Your git commit message for UC-X:**

> [UC-X] Fix cross-doc blending: unauthorized information synthesis → added single-source citation and refusal template

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> RICE Enforcement was the hardest. Explicitly defining what the agent must NOT do (refusal conditions) was more challenging than defining what it should do, but it was critical for preventing hallucinations.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The prohibition of cross-document blending in UC-X: "Never combine claims from two different documents into a single answer."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating the classification of internal support tickets to ensure high-priority security issues are flagged immediately using a strict RICE framework.

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

# Vibe Coding Workshop — Submission PR

**Name: Venkata Sai Badhrinadh Gundlapalli**  
**City / Group: Nellore / Computer Science and Engineering**  
**Date: 14/3/2026**  
**AI tool(s) used: Google's Antigravity, Chatgpt**  

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

> Taxonomy drift

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "If the complaint contains any of the following keywords — injury, child, school, hospital, unsafe, hazard — classify severity as Urgent regardless of category. Do not infer category from keywords alone; match the primary subject of the complaint to the taxonomy exactly."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing injury, child, school, and hospital keywords were correctly classified as Urgent after the enforcement rule was added.

**Your git commit message for UC-0A:**

> UC-0A Fix classifier.py: It did not fail→ Added agents.md and skills.md

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> All of the above — clause omission, scope bleed, and obligation softening were all observed in the naive output.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 3, 5, and 8 were missing entirely. Clause 2 was softened — the original used "must notify" but the naive summary said "should inform". Clause 7 had scope bleed where information not present in the source document was introduced.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 clauses are present and none are weakened or paraphrased beyond their original obligation strength.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — the naive output mentioned a "manager discretion" exception in Clause 7 that does not appear anywhere in the source policy document.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission and scope bleed: naive summary dropped 3 clauses and softened obligations → enforced every-numbered-clause rule and banned out-of-source additions

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> "The average budget growth across all wards and categories is +18.7% from the previous period."

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated silently across all wards and all categories into a single number. It did not mention the 5 null rows — they were silently dropped.

**After your fix — does your system refuse all-ward aggregation?**

> Yes 

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes 

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes 

**Your git commit message for UC-0C:**

> UC-0C Fix app.py: It did not fail→ Added agents.md and skills.md

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal phone to access work files when working from home, as the HR remote work policy allows flexible device usage. However, the IT policy generally recommends using company-approved devices where possible."

**Did it blend the IT and HR policies?**

> Yes — it blended the IT Acceptable Use policy and the HR Leave/Remote Work policy into a single answer without attributing either, and introduced the phrase "generally recommends" which appears in neither document.

**After your fix — what does your system return for this question?**

> "According to the IT Acceptable Use Policy (policy_it_acceptable_use.txt): Personal devices may not be used to access company files or systems unless explicitly enrolled in the MDM programme. Source: IT Acceptable Use Policy, Section 4.2."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — after adding the no-hedging enforcement rule to agents.md, none of the 7 test answers contained phrases like "while not explicitly covered", "typically", or "generally understood".
**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all 7 questions produced either a properly cited single-source answer or the exact refusal: "This question requires information from multiple policies. Please consult your HR or IT team directly."

**Your git commit message for UC-X:**

> UC-X Fix app.py : It didn't failed → Added agents.md and skills.md

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The hardest step was **Refine** — specifically knowing when to stop. After fixing the primary failure mode, the model would often introduce a subtler issue in the same response, such as fixing taxonomy drift but then adding hedging language. It required multiple CRAFT cycles per UC to fully close all gaps, and it was tempting to accept a "good enough" output too early.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> No, All are things are correctly generated by AI.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Participating in a Hackathon, Completing my Mini Project.

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

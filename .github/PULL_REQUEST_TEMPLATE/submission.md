# Vibe Coding Workshop — Submission PR

**Name:** Gayathiri
**City / Group:** Vellore
**Date:** 14 August 2026
**AI tool(s) used:** Antigravity IDE (Gemini)

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

> "Priority must be Urgent if the description contains any of these severity keywords (case-insensitive): injury, child, school, hospital (including hospitalised/hospitalized), ambulance, fire, hazard, fell (including fall/falling/fallen), collapse. Otherwise Standard (or Low for minor noise complaints only)."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> TBD out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: hospitalised not matching hospital regex → expanded pattern to include hospitalised/hospitalized morphological variants

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (omitted one of the two mandatory approvers: Department Head and HR Director) and Clauses 2.6 & 2.7 (softened carrying forward limits/dates).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes, phrases like "typically in government organisations" or "standard practice" were bled into the summary.

**Your git commit message for UC-0B:**

> [UC-0B] Implement policy summarization: completed clause summaries mapping and output generator

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated growth rate for all wards combined instead of splitting by ward and category, and it skipped the null actual_spend rows without flagging.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards, and no, it did not mention the null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes, flagged with 'NULL_DATA' and notes the reason from the notes column.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> [UC-0C] Fix YoY calculation: replaced hardcoded 2024 placeholder with dynamic YoY comparison using same-month lookup

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It blended the IT policy (personal device access) and HR policy (remote work tools), giving unauthorized access permissions.

**Did it blend the IT and HR policies?**

> Yes

**After your fix — what does your system return for this question?**

> Based on policy_it_acceptable_use.txt: Section 3.1: Employees may access CMC email and the employee self-service portal using personal devices. Section 3.2: Accessing other internal CMC systems, databases, or work files from personal devices is strictly prohibited.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> [UC-X] Implement Q&A agent: added document retrieval, keyword matching, and strict single-source citation rules

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Refine and Align steps were the hardest. Identifying corner cases (like edge-case morphological variations of words like 'hospitalised') and ensuring the rules in agents.md were correctly enforced by skills.md without introducing new bugs required careful testing.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The specific refusal template for UC-X and the strict rule preventing cross-document blending, which ensure the model refuses to answer questions not covered rather than hallucinating with hedging phrases.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating standard document review and parsing contracts or support ticket classification.

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

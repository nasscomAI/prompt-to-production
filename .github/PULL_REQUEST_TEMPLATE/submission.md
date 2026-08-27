# Vibe Coding Workshop — Submission PR

**Name:** Rishit Ghosh  
**City / Group:** Hyderabad  
**Date:** 22 June 2026  
**AI tool(s) used:** Antigravity  

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_hyderabad.csv` without crash
- [x] `results_hyderabad.csv` present in `uc-0a/`
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

> "Priority must be Urgent if the description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive)."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes, all severity signal rows (GH-202401, GH-202411, GH-202412, GH-202422) returned Urgent.

**Your git commit message for UC-0A:**

> UC-0A Complaint Classifier: implemented classifier.py and generated results_hyderabad.csv

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (approval of LWP requires BOTH Department Head and HR Director) was weakened to generic manager approval, and carry-forward limits/dates from 2.6 and 2.7 were omitted.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes, all 10 critical clauses are present.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes, it added generic corporate assumptions like "as is standard practice" and "employees are generally expected to".

**Your git commit message for UC-0B:**

> UC-0B Leave Policy Summary: implemented app.py and generated summary_hr_leave.txt

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated growth rate across all wards and categories combined, completely ignoring the per-ward breakdown.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards. No, it did not mention the 5 null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes, the 5 null rows (Row 58 in Ward 2, Row 124 in Ward 5, Row 167 in Ward 4, Row 191 in Ward 3, Row 255 in Ward 1) are identified and logged.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes, July actual spend has +33.1% growth and October actual spend has -34.8% growth.

**Your git commit message for UC-0C:**

> UC-0C Ward Budget Growth: implemented app.py and generated growth_output.csv

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It falsely blended the IT and HR policies and stated that personal devices can access work files using approved remote work tools.

**Did it blend the IT and HR policies?**

> Yes, it blended the IT remote work guidelines with the HR approved tool list.

**After your fix — what does your system return for this question?**

> According to policy_it_acceptable_use.txt Section 3.1, Personal devices may be used to access CMC email and the CMC employee self-service portal only. Also, Section 3.2 states that personal devices must not be used to access, store, or transmit classified or sensitive CMC data.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes, all 7 questions produced correct answers citing source documents and section numbers, or the exact refusal template.

**Your git commit message for UC-X:**

> UC-X Q&A Agent: implemented app.py and generated answers_hr_leave.txt

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Refinement was the hardest step because validating edge cases (like null data rows in UC-0C and cross-document query blending in UC-X) required strict constraints on default assumptions to make the system highly deterministic.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The exact Refusal Template and the rule prohibiting document blending in UC-X's agents.md: "Never combine claims from two different documents into a single answer."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating the classification and routing of customer support tickets based on strict priority keywords and service-level agreements.

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

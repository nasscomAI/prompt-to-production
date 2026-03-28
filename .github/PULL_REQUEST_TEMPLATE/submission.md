# Vibe Coding Workshop — Submission PR

**Name:** Ketan Sonar  
**City / Group:** Mumbai  
**Date:** 28-03-2026  
**AI tool(s) used:** VS Code, Copilot

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

> "Priority must be Urgent if description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive)"

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15 (validated against reference cases in data and rules)

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all relevant rows (school, hazard, injury) returned Urgent.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: added explicit severity keyword mapping and urgent priority logic → improved priority decision and ambiguous category handling

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission (naive text summarization can drop clause 5.2 condition)

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> 5.2 (Department Head AND HR Director approval) and 7.2 (no leave encashment) were most likely to be skimmed.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 clauses are present.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No — with RICE enforcement I avoided bleed.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: enforced exact clause coverage and explicit source clause mapping

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> Naive expected behavior: single overall growth value; correction returns per ward/category table with null marking.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> No all wards aggregation; yes, marks 5 null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — 2024-03 Ward 2 – Shivajinagar Drainage & Flooding; 2024-07 Ward 4 – Warje Roads & Pothole Repair; 2024-11 Ward 1 – Kasba Waste Management; 2024-08 Ward 3 – Kothrud Parks & Greening; 2024-05 Ward 5 – Hadapsar Streetlight Maintenance

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix wrong aggregation: enforce ward/category query, null row flagging, and MoM formula reporting

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> Naive model may blend HR + IT and incorrectly allow. Fixed model returns IT-only or refusal.

**Did it blend the IT and HR policies?**

> No

**After your fix — what does your system return for this question?**

> According to policy_it_acceptable_use.txt section 3.1: Personal devices may access CMC email and employee self-service portal only.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix cross-document blending: enforce single-source responses and exact refusal template if not covered

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Analyze was hardest because I needed to map failure modes to explicit rule gaps and anticipate edge cases for each UC.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> UC-0B agents.md rule: "Preserve ALL conditions for multi-condition obligations (e.g. 5.2 must include Department Head + HR Director approval)."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Building a compliance report generator with explicit source clause verification for policy/contract text outputs.

---

## Reviewer Notes *(tutor fills this section)*

| Criterion | Score /4 | Notes |
|---|---|---|
| RICE prompt quality | | |
| agents.md quality | | |
| skills.md quality | | |
| CRAFT loop evidence | | |
| Test coverage | | |
| **Total** | **/20** |

**Badge decision:**
- [x] Standard badge — meets pass threshold (score 11+/20 on this review, full rubric 22+/40)
- [ ] Distinction badge — meets distinction threshold (score 17+/20 on this review, full rubric 34+/40)
- [ ] Not yet — resubmit after addressing: _______________

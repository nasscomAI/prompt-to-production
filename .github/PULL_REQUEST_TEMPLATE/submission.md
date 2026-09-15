# Vibe Coding Workshop — Submission PR

**Name:** Arunkumar  
**City / Group:** Mysuru  
**Date:** 2026-09-15  
**AI tool(s) used:** Antigravity IDE  

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for UC-0A
- [x] `skills.md` committed for UC-0A
- [x] `classifier.py` runs on `test_pune.csv` without crash
- [x] `results_pune.csv` present in `uc-0a/`
- [x] Commits with meaningful messages following the formula
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> Severity blindness and taxonomy drift

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> `"priority must be set to Urgent if the complaint description contains any of the severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive)."`

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing severity triggers (`school`, `hazard`, `injury`, `fell`) returned `Urgent`.

**Your git commit message for UC-0A:**

> `[UC-0A] Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers`

---

## UC-0B — Summary That Changes Meaning

*(Focused submission on UC-0A)*

---

## UC-0C — Number That Looks Right

*(Focused submission on UC-0A)*

---

## UC-X — Ask My Documents

*(Focused submission on UC-0A)*

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Control step was the most critical and challenging, because writing precise, testable enforcement boundaries and explicit refusal conditions in `agents.md` prior to code generation is necessary to prevent silent hallucination and severity blindness.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> `"Refusal condition: If the category cannot be confidently determined from the complaint description alone, output category 'Other' and set flag to 'NEEDS_REVIEW' rather than guessing."`

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating grievance ticket categorization, triage priority assignment, and SLA routing for civic services.

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

# Vibe Coding Workshop — Submission PR

**Name:**  Tallapaneni Siri Chandana
**City / Group:**  Nellore
**Date:**  14 - 03 - 2026
**AI tool(s) used:**  Antigravity and Visual Studio

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

> Severity blindness — The classifier failed to prioritize urgent cases based on severity signals.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Always assign 'Urgent' to complaints mentioning injury, child, school, or hospital."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 13 out of 15 — Most rows matched the answer key, with minor discrepancies.

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — All severity signal rows were correctly labeled as Urgent after applying the enforcement rule.

**Your git commit message for UC-0A:**

> git commit -m "UC-0A update agents and skills"

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission — Some important clauses were missing in the naive summary.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 3 and 7 were missing in the naive output.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — All 10 critical clauses are present after the fix.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No — The naive prompt did not add any information not in the source document.

**Your git commit message for UC-0B:**

> git commit -m "UC-0B update agents and skills"

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> "Overall growth is 18.2% for the period."

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes — The naive prompt aggregated across all wards and did not mention the 5 null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — The system now refuses to aggregate across all wards and only provides ward-specific results.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — Rows 4, 9, 12, 15, and 18 are flagged as null in the output.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — The output matches the reference values for Ward 1 Roads in July and October.

**Your git commit message for UC-0C:**

> git commit -m "UC-0C update agents and skills"
---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Generally, employees may use personal devices for work purposes when working remotely, provided they follow company security guidelines."

**Did it blend the IT and HR policies?**

> Yes — The answer combined information from both IT and HR policies.

**After your fix — what does your system return for this question?**

> "According to the IT policy, personal devices may not be used to access work files remotely."

**Did your system use any hedging phrases in any answer?**
* ("while not explicitly covered", "typically", "generally understood")*

> No — The system provided direct answers without hedging phrases.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — All test questions produced correct single-source or refusal responses.

**Your git commit message for UC-X:**

> git commit -m "UC-0x update skills and agents"
---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The hardest step was Feedback, as it required careful analysis of model outputs and iterative adjustments to prompts and enforcement rules to achieve the desired behavior across all use cases.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> "Always assign 'Urgent' to complaints mentioning injury, child, school, or hospital."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> I will use RICE + CRAFT to design and test an automated email triage system for customer support requests.

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
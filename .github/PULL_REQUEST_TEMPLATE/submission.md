# Vibe Coding Workshop — Submission PR

**Name:** Sheema Md
**City / Group:** SheemaMd-Nellore
**Date:** March 15, 2026
**AI tool(s) used:** Google Gemini / Antigravity

---

## Checklist — Complete Before Opening This PR

- [X] `agents.md` committed for all 4 UCs
- [X] `skills.md` committed for all 4 UCs
- [X] `classifier.py` runs on `test_[city].csv` without crash
- [X] `results_[city].csv` present in `uc-0a/`
- [X] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [X] `summary_hr_leave.txt` present in `uc-0b/`
- [X] `growth_output.csv` present in `uc-0c/`
- [X] 4+ commits with meaningful messages following the formula
- [X] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> Severity blindness

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> Strict Priority Override: If the complaint text contains explicit high-severity keywords such as 'school', 'hospital', 'injury', or 'accident', the 'priority' categorizer MUST be set to 'Urgent' regardless of the standard algorithm.

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — explicit logic was implemented to intercept these keywords and enforce the output "Urgent".

**Your git commit message for UC-0A:**

> [UC-0A] Fix severity blindness: naive logic missed critical contexts → added strict priority enforcement for keywords like injury, school, and hospital

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and dropping of conditions

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 2.4, 2.7, 3.4 were highly susceptible to dropping, and Clause 5.2 frequently lost the dual-approver condition (dropping the HR Director requirement).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No — the RICE rules mathematically enforced verbatim extraction for the required clauses, completely preventing scope bleed.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: text summarization dropped conditions → enforced verbatim extraction of the 10 core clauses to prevent meaning loss

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> A single global percentage combining all wards and categories simultaneously without detailing any formulas.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it illegally aggregated across all wards, and it silently skipped or hallucinated data for the 5 null rows without flagging them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — For example, when testing Ward 4, the output for July specifically output: `Cannot compute: current period is NULL` and `[FLAG] NULL value: Audit freeze — figures under review`.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: formula assumed and nulls ignored → enforced explicit ward/category filtering, MoM formula output, and null flagging

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal phone to access allowed remote work files and emails."

**Did it blend the IT and HR policies?**

> Yes — It inappropriately blended HR's general allowance for "remote work tools" with IT's highly specific device-access rules.

**After your fix — what does your system return for this question?**

> "You may only access CMC email and the employee self-service portal on personal devices. (policy_it_acceptable_use.txt - Section 3.1)"

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix cross-document blending: AI merged IT device rules with HR remote rules → enforced single-source citation and strict refusal template

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The 'Refine' step was consistently the hardest because it required switching from standard conversational prompt engineering to thinking strictly in terms of testable negative constraints and absolute rule enforcement, which feels unnatural at first.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> In UC-X, explicitly enforcing the exact verbatim refusal template string without variations or apologies was the only way to mathematically eliminate hedging and hallucinations when the agent lacked the correct policy information.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automatically parsing and classifying incoming customer feedback emails into actionable feature requests or bug reports based on explicit keywords and rigid output schemas.

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

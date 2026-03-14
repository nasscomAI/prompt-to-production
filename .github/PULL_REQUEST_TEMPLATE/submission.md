# Vibe Coding Workshop — Submission PR

**Name:** Shivansh Mishra
**City / Group:** Lucknow
**Date:** March 14, 2026
**AI tool(s) used:** Antigravity

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

> false confidence

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "If the category is genuinely ambiguous or cannot be determined from the description alone, set the flag field to NEEDS_REVIEW (otherwise leave blank)."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — explicit keyword matching was forced for severity handling.

**Your git commit message for UC-0A:**

> UC-0A Fix false confidence: AI classified ambiguous rows without flagging them -> Enforced exactly one allowed category or strict fallback to Other with NEEDS_REVIEW flag

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> condition dropping (obligation softening)

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (Naive prompt often dropped the requirement for BOTH Department Head and HR Director)

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — explicitly extracted and cited verbatim.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added phrases like "as is standard practice" which scope bleed.

**Your git commit message for UC-0B:**

> UC-0B Fix condition dropping: AI dropped the HR Director from the double-approval requirement -> Enforced verbatim quoting and strict inclusion of all original multi-condition binding clauses without softening

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated percentage for all wards combined.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards. No, it silently skipped the null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — 'NULL FLAGGED - Reason: [notes]' is populated for the 5 rows.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix silent null handling: AI calculated growth using skipped or zero-filled nulls -> Enforced strict flagging of nulls with note reason and outright refusal of multi-ward aggregation

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, personal phones can be used for approved remote work tools and email."

**Did it blend the IT and HR policies?**

> Yes — blending remote work tools from HR policy and email usage from IT policy into a single affirmative authorization.

**After your fix — what does your system return for this question?**

> "Personal devices may access CMC email and the employee self-service portal only. Source: policy_it_acceptable_use.txt (Section 3.1)"

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix cross-document blending: AI hallucinated permissions by combining HR and IT policies -> Implemented strict single-source citation enforcement and a verbatim refusal template for unanswerable/blended queries

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The 'Refining Enforcement' phase. Nailing the exact binding language to ensure the LLM wouldn't find loopholes (like dropping the second approver in UC-0B while retaining the first) required rigorous trial-and-error context building.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> Stating the exact verbatim wording for the refusal template in UC-X to prevent "helpful hedging" ("This question is not covered in the available policy documents...").

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Defining constraints for automated compliance evaluation on internal pull-requests.

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

# Vibe Coding Workshop — Submission PR

**Name:** Mohit Polisetty
**City / Group:** Hyderabad
**Date:** 2026-03-09
**AI tool(s) used:** Antigravity (Google DeepMind)

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
*severity blindness*

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**
> **Severity Enforcement**: Any description containing keywords like `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, or `collapse` MUST be marked as **Urgent**.

**How many rows in your results CSV match the answer key?**
15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**
Yes - Ambulance diverted, Rider hospitalised, School bus potholes, Road collapsed - all correctly marked Urgent.

**Your git commit message for UC-0A:**
> UC-0A Fix severity blindness: naive classification missed critical keywords → implemented keyword-based priority uplift for safety-critical terms

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*clause omission*

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**
Clause 5.2 was weakened (missing the 'BOTH' approvers condition), and Clause 7.2 was often omitted in standard summaries.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**
Yes.

**Did the naive prompt add any information not in the source document (scope bleed)?**
Yes - "as is standard practice" and "typically" phrases were removed after enforcement.

**Your git commit message for UC-0B:**
> UC-0B Fix clause omission: completeness not enforced in naive summary → added logic to ensure every criticalNumbered clause is preserved including multi-condition approvers

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**
One single percentage for all wards combined, ignoring the NULL rows.

**Did it aggregate across all wards? Did it mention the 5 null rows?**
It aggregated all wards and silently skipped null rows without reporting them.

**After your fix — does your system refuse all-ward aggregation?**
Yes.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**
Yes - rows for Ward 1 Waste Management (2024-11) and others are flagged in the Formula/Growth columns.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**
Yes - 2024-07: +33.1%, 2024-10: -34.8%.

**Your git commit message for UC-0C:**
> UC-0C Fix silent aggregation: no scope enforcement in naive calculation → implemented strict per-ward per-category filtering and formula transparency

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
"Yes, personal phones can be used for approved remote work tools and email."

**Did it blend the IT and HR policies?**
Yes - it combined permission for "approved tools" from HR with "personal devices" from IT.

**After your fix — what does your system return for this question?**
> Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.
> Source: policy_it_acceptable_use.txt Section 3.1

**Did your system use any hedging phrases in any answer?**
No.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**
Yes.

**Your git commit message for UC-X:**
> UC-X Fix cross-doc blending: naive Q&A combined contradictory rules → implemented single-source enforcement and refusal template for out-of-scope queries

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**
Enforcement (Logic refinement). It was challenging to ensure the model didn't "soften" the rules when summarizing or answering questions across different documents.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**
> **Single-Source Integrity**: Never combine information from different documents to form a composite answer.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**
Analyzing customer support logs and classifying them according to our internal service level taxonomy.

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

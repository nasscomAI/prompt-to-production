# Vibe Coding Workshop — Submission PR

**Name:**  Ashwin Dutta
**City / Group:**  Pune
**Date:**  18-04-2026
**AI tool(s) used:**  Antigravity / Gemini

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

> Severity blindness. The naive prompt classified complaints mentioning "school children" and "injury" as Standard instead of Urgent.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be Urgent if the description contains ANY of these severity keywords (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Presence of even one keyword forces Urgent."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — PM-202402 (school children), PM-202411 (electrical hazard), PM-202420 (injury), and PM-202446 (elderly fell) all correctly returned Urgent.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and obligation softening (condition dropping).

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 was weakened. It dropped the requirement for the HR Director's approval and only mentioned the Department Head.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes, all 10 clauses are preserved with near-verbatim accuracy.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes, it added phrases like "as is standard company practice" when discussing Leave Without Pay.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause rule with multi-condition preservation

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single, all-ward aggregated growth number, blending all categories together into one meaningless percentage, while silently skipping the null rows.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards. No, it entirely ignored the 5 null rows without flagging them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 null rows are flagged with `NULL_DATA` and their reasons from the notes (e.g., "Equipment procurement delay", "Audit freeze").

**Does your output match the reference values (Ward 1 Roads +33.1% in July, -34.8% in October)?**

> Yes. 

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only with null flagging

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It blended IT Policy 3.1 and portions of the HR WFH policy to wrongfully infer: "Yes, you can use your personal phone to access work files if working from home permanently."

**Did it blend the IT and HR policies?**

> Yes.

**After your fix — what does your system return for this question?**

> "According to policy_it_acceptable_use.txt, Section 3.1... personal devices may be used to access CMC email and the CMC employee self-service portal ONLY. Accessing general 'work files' beyond email and the self-service portal is not permitted on personal devices."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes.

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: no single-source rule → added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Enforcement step in drafting the RICE prompt. It was challenging to write rules that were completely airtight and testable without accidentally introducing new loopholes or logic traps for the LLM. 

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The exact wording of the refusal template in UC-X: "If a question is not covered in any of the three documents, use the refusal template EXACTLY: 'This question is not covered...'" The AI natively wants to be helpful and hedge rather than shutting down the inquiry.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Building an automated log-analysis script that flags specific error thresholds without hallucinating root causes.
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

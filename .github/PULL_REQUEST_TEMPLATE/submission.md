# Vibe Coding Workshop — Submission PR

**Name:** Ratul Shee  
**City / Group:** WB  
**Date:** 2026-09-15  
**AI tool(s) used:** Antigravity AI Pair Programmer  

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

> Severity blindness and taxonomy drift.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> `"Priority must be set to Urgent if the description contains any of the severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise set to Standard or Low based on severity."`

**How many rows in your results CSV match the answer key?**

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all complaints containing severity keywords (such as PM-202402 with 'school'/'child', PM-202411 with 'hazard', PM-202420 with 'injury', and PM-202446 with 'fell') returned Urgent.

**Your git commit message for UC-0A:**

> `UC-0A Fix severity blindness: no keywords in enforcement -> added injury/child/school/hospital triggers`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**

> Clause omission and obligation softening (e.g. dropping dual approval roles for LWP in clause 5.2).

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 2.5, 2.7, 3.4, 5.2 (softened from requiring Department Head AND HR Director to 'requires approval'), and 7.2.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 critical clauses are explicitly referenced and preserved without condition loss.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — added phrases like "as per standard government practice" and "typically subject to HR discretion" which are absent from `policy_hr_leave.txt`.

**Your git commit message for UC-0B:**

> `UC-0B Fix clause omission: completeness not enforced -> added every-numbered-clause rule`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> Returned a single aggregated growth number (+12.4%) for the entire municipal budget without distinguishing wards or categories.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all 5 wards silently and ignored/skipped the 5 null rows without flagging them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — returns explicit refusal error if `--ward All` or global aggregation is attempted.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — outputs `NULL` actual spend and `NULL` growth percentage, while recording the reason from the notes column in the `flag` field.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — Ward 1 Kasba Roads & Pothole Repair returned +33.1% for 2024-07 and −34.8% for 2024-10.

**Your git commit message for UC-0C:**

> `UC-0C Fix silent aggregation: no scope in enforcement -> restricted to per-ward per-category only`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal phone for approved remote work tools and email under HR and IT policies."

**Did it blend the IT and HR policies?**

> Yes — blended IT policy section 3.1 with HR remote work policy to grant permission that does not exist in the source documents.

**After your fix — what does your system return for this question?**

> `"According to policy_it_acceptable_use.txt (Section 3.1 & 3.2): Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."`

**Did your system use any hedging phrases in any answer?**

> No — zero hedging phrases used across all 7 test cases.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all 7 test questions returned either a single-source answer with document name and section citation or the exact refusal template.

**Your git commit message for UC-X:**

> `UC-X Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The **Analysis of Failure Modes** step was hardest because subtle failure modes (like condition dropping in multi-approver clauses or scope bleed in RAG) sound plausible on first glance and require systematic test cases to expose.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The exact, mandatory refusal template for UC-X: `"This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."`

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Applying RICE enforcement and CRAFT evaluation loops to automated internal document summarization and policy compliance audit reporting.

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


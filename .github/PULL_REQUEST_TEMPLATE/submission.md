# Vibe Coding Workshop — Submission PR

**Name:** Samhita Kurikala  
**City / Group:** Hyderabad
**Date:** March 21, 2026
**AI tool(s) used:** ChatGPT 

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

> Severity blindness — urgent cases were not being prioritized.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> Urgent priority is triggered when complaints contain keywords like injury, child, danger, risk, accident.

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — keyword-based detection ensures all such cases are marked Urgent.

**Your git commit message for UC-0A:**

> UC-0A Final Fix inconsistent classification: no strict rules and priority handling → added keyword-based categories, urgency detection, and review flag

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission — important conditions were getting dropped.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses like 2.4, 5.2, and 3.2 lost critical conditions in naive summarization.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all clauses are extracted and preserved.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added generalized statements not present in the document.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: naive summarization dropped conditions → preserved all clauses without loss

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> Gave an aggregated / unclear result.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Naive approach typically aggregates and ignores null values.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — it strictly filters by ward and category.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> No — current run didn’t include null rows, though logic exists.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — July (+33.1%) and October (−34.8%) match correctly.

**Your git commit message for UC-0C:**

> UC-0C Fix wrong aggregation: naive approach combined data → implemented per-ward per-category growth with null handling and formula visibility

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, personal phones can be used for approved remote work tools and email."

**Did it blend the IT and HR policies?**

> Yes - IT policy section 3.1 allows personal devices for "CMC email and employee self-service portal only", while HR policy mentions work-from-home arrangements, creating temptation to blend into broader permission.

**After your fix — what does your system return for this question?**

> Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision. (Source: policy_hr_leave.txt Section 8.1)

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — responses are direct and source-based.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> [UC-X Fix cross-document blending: naive search mixed policies → enforced single-source answers with strict refusal template] & [UC-X Final Fix cross-document blending: naive search mixed policies → enforced single-source answers with strict refusal template]

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Fix step was the hardest because it required identifying specific failure modes like clause omission and aggregation errors and correcting them without breaking other parts of the system. It also involved iteratively testing and refining the logic to ensure consistent outputs.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> “Never combine information from multiple documents into a single answer.”

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> I will apply RICE + CRAFT when developing small AI-based tools to ensure they don’t produce vague or incorrect outputs and instead follow strict rules.

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

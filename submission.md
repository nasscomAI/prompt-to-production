# Vibe Coding Workshop — Submission PR

**Name: Santhosh Kumar
**City / Group: Bangalore
**Date: 19-09-2026
**AI tool(s) used: opencode / big-pickle

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

> taxonomy drift, severity blindness, missing justification, false confidence

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — exact strings only, no variations, no sub-categories.

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> Tutor release out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes

**Your git commit message for UC-0A:**

> UC-0A Fix taxonomy drift, severity blindness, missing justification, hallucinated sub-categories, false confidence on ambiguity: naive prompt would vary category names across rows, downgrade injury/child/school complaints to Standard, omit reason fields, invent sub-categories, and guess confidently on ambiguity -> implemented classifier.py with exact 10-value categories only, severity-keyword Urgent priority, one-sentence reasons quoting description words, and Other+NEEDS_REVIEW refusal on multi-category ambiguity, plus filled agents.md and skills.md

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

>  Fix clause omission, scope bleed, obligation softening

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> 5.2 (approvers preserved), 2.4 (written approval before leave)

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No

**Your git commit message for UC-0B:**

>  UC-0B Fix clause omission, scope bleed, obligation softening: naive summary dropped clauses (e.g. 3.2, 5.2), softened binding verbs like must/will/not permitted, and injected external HR norms -> built app.py with retrieve_policy + summarize_policy that restates all 28 clauses by number with binding verbs and all conditions intact (both 5.2 approvers preserved), quotes verbatim and flags NEEDS_REVIEW when restatement risks meaning loss, plus filled agents.md and skills.md

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> Output not returned

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Started however process incomplete

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes
  2024-03 | Ward 2 � Shivajinagar | Drainage & Flooding | notes: Data not submitted by ward office
  2024-05 | Ward 5 � Hadapsar | Streetlight Maintenance | notes: Equipment procurement delay
  2024-07 | Ward 4 � Warje | Roads & Pothole Repair | notes: Audit freeze � figures under review
  2024-08 | Ward 3 � Kothrud | Parks & Greening | notes: Project suspended � pending approval
  2024-11 | Ward 1 � Kasba | Waste Management | notes: Contractor change � billing delayed

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix wrong aggregation level, silent null handling, formula assumption: naive prompt returned one all-ward number, ignored the 5 null rows, and silently picked a growth formula -> built app.py with load_dataset + compute_growth that flags every null row with its notes reason before computing, refuses cross-ward/category aggregation, shows the exact formula on every row, reproduces reference values (+33.1%/-34.8%), and refuses when --growth-type is missing or unsupported (MoM only; YoY refused for lack of baseline), plus filled agents.md and skills.md


---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> Naive output not saved

**Did it blend the IT and HR policies?**

> Yes, it was pre-fix failure mode

**After your fix — what does your system return for this question?**

> According to policy_it_acceptable_use.txt section 3.1: Personal devices may be used to access CMC email and the CMC employee self-service portal only

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> Yes

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

>  UC-X Fix cross-document blending, hedged hallucination, condition dropping: naive prompt blended HR and IT in the personal-phone question and hedged with phrases like typically or generally understood -> built app.py with retrieve_documents + answer_question that answers from exactly ONE document with document-name + section citation or the verbatim refusal template, never blends two documents, never hedges, and preserves multi-condition obligations (5.2 needs both approvers), plus filled agents.md and skills.md

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Refinement proved hardest because outputs passed initial visual checks despite breaking strict constraints like dropped conditions, blended citations, or silent nulls. Engineering deterministic checks to enforce these boundaries took the most effort.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> Clubbing multple docs into one

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> For SDLC life cycle & validation

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

# Vibe Coding Workshop — Submission PR

**Name:** Gabriel Luanzon 
**City / Group:** Manda  
**Date:** August 12, 2026 
**AI tool(s) used:**  Gemini 2.0 Flash 

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

> severity blindness and taxonomy drift

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be Urgent if description contains any of the 9 severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise Priority must be Standard."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all complaints containing severity trigger words returned Urgent priority without exception.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness and taxonomy drift: placeholder RICE and naive classifier -> implemented strict RICE rules, severity triggers, verbatim citations, and multi-category ambiguity flagging

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission and obligation softening

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 2.5 (unapproved absence = LOP), Clause 2.7 (Q1 carry-forward deadline), Clause 3.4 (sick leave around holidays), Clause 5.2 (weakened by dropping HR Director approver), and Clause 7.2 (prohibition of in-service leave encashment).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 critical binding clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are fully present with strict binding verbs and complete dual-approval conditions.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — the naive output added scope bleed phrases such as "as is standard practice in municipal government" and "employees are generally expected to comply".

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission and obligation softening: naive summarizer dropped approvers and binding verbs -> implemented complete clause retrieval, binding verb enforcement, and dual approver rules

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> "Total budget growth across all wards for 2024 is +8.4%."

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated all 5 wards and 5 categories into a single composite number, completely ignoring the 5 null actual_spend rows without mention.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — the system explicitly refuses all-ward and cross-category aggregation requests and demands specific --ward and --category parameters.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 null rows (2024-03 Ward 2 Drainage, 2024-07 Ward 4 Roads, 2024-11 Ward 1 Waste, 2024-08 Ward 3 Parks, 2024-05 Ward 5 Streetlight) are flagged as N/A (Data Missing) with their notes included.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — Ward 1 Roads & Pothole Repair returned exactly +33.1% for 2024-07 (monsoon spike) and -34.8% for 2024-10 (post-monsoon).

**Your git commit message for UC-0C:**

> UC-0C Fix wrong aggregation level and silent null handling: naive tool aggregated all wards and ignored nulls -> implemented per-ward per-category scope, explicit null flagging, and formula auditing

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, personal phones can be used for approved remote work tools and email when working from home, provided company policies are followed."

**Did it blend the IT and HR policies?**

> Yes — it blended IT policy device rules with HR remote work guidelines to construct a permissive policy claim that does not exist in either source document.

**After your fix — what does your system return for this question?**

> "According to policy_it_acceptable_use.txt (Section 3.1 & 3.2), personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must NOT be used to access, store, or transmit classified or sensitive CMC data or work files."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — zero hedging vocabulary was used across all responses.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all 7 benchmark questions produced exact single-source section citations or the verbatim refusal template.

**Your git commit message for UC-X:**

> UC-X Fix cross-document blending and hedged hallucination: naive QA blended IT and HR policies -> implemented single-source attribution, exact refusal template, and section citations

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Focus and Refine steps were the most critical and challenging across all UCs. Eliminating subtle AI failure modes like multi-category ambiguity in UC-0A, condition drops in UC-0B policy summaries, and cross-document blending in UC-X required writing explicit negative constraints and exact refusal conditions in agents.md.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The explicit Verbatim Refusal Template in UC-X agents.md: `"This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the relevant team for guidance."` This prevented hedged hallucinations on out-of-scope queries.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automated document analysis and policy compliance auditing for internal standard operating procedures and municipal operations.

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

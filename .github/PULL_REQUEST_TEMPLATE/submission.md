# Vibe Coding Workshop — Submission PR

**Name:** Harsh Kumar  
**City / Group:** New Delhi  
**Date:** 2026-09-08  
**AI tool(s) used:** Google Antigravity  

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

> Severity blindness and taxonomy drift. The unguided prompt classified high-risk complaints (e.g., potholes risking schoolchildren and collapsing structures) as Standard rather than Urgent, and invented unapproved category labels like "Public Safety Hazard".

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "category must strictly be one of the allowed enum values: 'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'. Exact strings only, no abbreviations, synonyms, or variations."  
> "priority must be set to 'Urgent' if the description contains any severity keyword: 'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse' (matched case-insensitively, including word stems and plurals)."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all safety signal rows (PM-202402 with 'school' and 'children', PM-202411 with 'hazard', PM-202420 with 'injury', PM-202446 with 'fell') returned Urgent priority without exception.

**Your git commit message for UC-0A:**

> `[UC-0A] Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and condition dropping (specifically Clause 5.2 losing the second mandatory approver).

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (weakened by dropping the HR Director approval requirement, stating only manager approval); Clause 2.4 (omitted the requirement that approval must be written before leave commences); Clause 2.7 (dropped the Jan–Mar usage window for carry-forward leave); Clause 7.2 (softened 'not permitted under any circumstances' into 'generally discouraged').

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) and all 25 numbered clauses (1.1 through 8.2) are explicitly preserved with exact thresholds and binding verbs.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — naive summaries added ungrounded assumptions such as "as is standard practice in government municipal bodies" and "employees are expected to inform informally ahead of time".

**Your git commit message for UC-0B:**

> `[UC-0B] Fix clause omission: completeness not enforced → added every-numbered-clause rule`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> "Overall municipal infrastructure expenditure grew by approximately 4.2% across all wards during 2024."

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it silently aggregated across all 5 wards into a single macro figure, picked a formula silently without asking, and completely skipped the 5 deliberate null rows without mentioning missing data.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — attempts to aggregate across all wards or all categories are explicitly refused with the error: "Refused: Aggregating across multiple wards obscures ward-level variances. Please specify an individual ward (e.g. 'Ward 1 – Kasba')."

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 deliberate null rows are reported upon loading and flagged in the output table as NULL_RECORD with the exact note cited:
> 1. 2024-03 · Ward 2 – Shivajinagar · Drainage & Flooding (Note: Data not submitted by ward office)
> 2. 2024-05 · Ward 5 – Hadapsar · Streetlight Maintenance (Note: Equipment procurement delay)
> 3. 2024-07 · Ward 4 – Warje · Roads & Pothole Repair (Note: Audit freeze – figures under review)
> 4. 2024-08 · Ward 3 – Kothrud · Parks & Greening (Note: Project suspended – pending approval)
> 5. 2024-11 · Ward 1 – Kasba · Waste Management (Note: Contractor change – billing delayed)

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — Ward 1 Kasba Roads & Pothole Repair matches exactly:
> - July 2024: 19.7 lakh, MoM Growth: +33.1% (Formula: ((19.7 - 14.8) / 14.8) * 100 = +33.1%)
> - October 2024: 13.1 lakh, MoM Growth: −34.8% (Formula: ((13.1 - 20.1) / 20.1) * 100 = -34.8%)

**Your git commit message for UC-0C:**

> `[UC-0C] Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you may use your personal phone to access work files when working from home, provided you use CMC approved remote work tools and adhere to standard data security precautions."

**Did it blend the IT and HR policies?**

> Yes — it merged IT device terms with HR remote work allowances, creating a fabricated permission that directly contradicts the IT policy restriction.

**After your fix — what does your system return for this question?**

> "Under CMC Acceptable Use Policy (Section 3.1 & 3.2), personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified, sensitive, or general CMC work files. [Citation: policy_it_acceptable_use.txt (Section 3.1, 3.2)]"

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — zero hedging phrases used. All 7 queries were audited and confirmed free of forbidden hedging expressions.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — Questions 1, 2, 3, 4, 6, and 7 returned precise single-source cited answers, and Question 5 (flexible working culture) returned the exact refusal template.

**Your git commit message for UC-X:**

> `[UC-X] Fix cross-doc blending: no single-source rule → added single-source attribution enforcement`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Analyze step was the most demanding because identifying subtle semantic failures — such as condition dropping in multi-approver workflows or cross-document policy blending — requires careful comparison against ground truth rather than accepting fluent, plausible-sounding AI responses.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The strict negative constraints prohibiting synthesis and hedging: "Never combine claims from two different documents into a single answer. Every factual response must derive entirely from a single source document" along with the verbatim refusal template. The AI initially preferred helpful interpolations over clean refusals.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Applying RICE + CRAFT to build an automated citizen grievance triage pipeline and municipal regulatory compliance auditor, ensuring automated summaries strictly preserve statutory constraints without hallucinating permissions or missing safety escalations.

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


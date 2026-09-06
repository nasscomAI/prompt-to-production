# Vibe Coding Workshop — Submission PR

**Name:** Supraja  
**City / Group:** Bengaluru  
**Date:** 2024-09-06  
**AI tool(s) used:** Antigravity IDE (Gemini)  

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

> Severity blindness and taxonomy drift. The naive prompt classified safety-critical issues (e.g. potholes near schools and fallen pedestrians) as Standard priority and hallucinated categories outside municipal schema.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be Urgent if the complaint description contains any of the severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise set to Standard or Low." and "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations or sub-categories permitted."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing triggers (e.g., PM-202402 with "School", PM-202411 with "hazard", PM-202420 with "injury", PM-202446 with "fell") correctly returned Urgent with quoted evidence.

**Your git commit message for UC-0A:**

> `[UC-0A] Fix severity blindness: missing keywords in enforcement -> added injury/child/school/hospital triggers`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Condition dropping and clause omission. The naive summary dropped the secondary approver in Clause 5.2 and softened binding verbs ("must" became "should").

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> - Clause 5.2: Preserved "requires approval" but dropped "both Department Head AND HR Director" (leaving only manager or single approver).
> - Clause 2.4: Dropped "verbal approval is not valid".
> - Clause 7.2: Softened "not permitted under any circumstances" into a general guideline.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 ground truth clauses and all 29 section clauses are explicitly enumerated and audited.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — the naive prompt introduced generalizations such as "as is standard practice in public sector organizations" and "employees are expected to plan ahead". Both were eliminated with zero scope bleed after enforcement.

**Your git commit message for UC-0B:**

> `[UC-0B] Fix condition drop: clause 5.2 lost second approver -> added multi-condition preservation rule`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> A single citywide average growth percentage across all wards combined, without breaking down by ward or category.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards and silently ignored the 5 null rows without flagging missing data.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — attempting to calculate across "All" wards or categories triggers an immediate refusal error requiring a specific ward and category.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 null rows are proactively detected, audited, and flagged:
> 1. 2024-03 | Ward 2 – Shivajinagar | Drainage & Flooding (Data not submitted by ward office)
> 2. 2024-05 | Ward 5 – Hadapsar | Streetlight Maintenance (Equipment procurement delay)
> 3. 2024-07 | Ward 4 – Warje | Roads & Pothole Repair (Audit freeze – figures under review)
> 4. 2024-08 | Ward 3 – Kothrud | Parks & Greening (Project suspended – pending approval)
> 5. 2024-11 | Ward 1 – Kasba | Waste Management (Contractor change – billing delayed)

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — July 2024 shows +33.1% and October 2024 shows −34.8% with explicit calculation formulas displayed in every row.

**Your git commit message for UC-0C:**

> `[UC-0C] Fix silent aggregation: no ward/category scope -> enforced per-ward per-category only`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal phone for approved remote work tools and CMC email when working from home."

**Did it blend the IT and HR policies?**

> Yes — it merged HR remote work statements with IT BYOD permissions, granting unapproved access to work files that is explicitly prohibited by IT policy.

**After your fix — what does your system return for this question?**

> "According to policy_it_acceptable_use.txt (Section 3.1), personal devices may be used to access CMC email and the CMC employee self-service portal only. Section 3.2 explicitly states that personal devices must not be used to access, store, or transmit classified or sensitive CMC data, and Section 5.1 prohibits storing Confidential or Restricted data on personal devices. Accessing work files on personal devices beyond email and the self-service portal is prohibited."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — zero hedging phrases used across all responses.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — Questions 1, 2, 3, 4, 6, 7 produced single-source cited answers with document and section references. Question 5 produced the exact refusal template.

**Your git commit message for UC-X:**

> `[UC-X] Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The **Analyze** and **Fix** steps were the most demanding. Spotting subtle AI errors — such as condition drops (e.g. silently omitting the HR Director from dual-approver requirements) or cross-document blending between HR and IT policies — required establishing strict deterministic enforcement rules rather than relying on soft conversational instructions.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The refusal enforcement rules: explicitly defining the verbatim refusal template for ungrounded questions in UC-X, and the strict non-aggregation prohibition in UC-0C to prevent silent pooling of municipal data.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Building an automated policy compliance and internal regulatory search assistant for standard operating procedures (SOPs), using single-source attribution and exact refusal constraints to eliminate compliance hallucinations.

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

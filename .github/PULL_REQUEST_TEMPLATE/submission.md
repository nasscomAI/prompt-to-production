# Vibe Coding Workshop — Submission PR

**Name:** Ankit Srivastav (thakurankitr@gmail.com)
**City / Group:** Pune
**Date:** 2026-07-15
**AI tool(s) used:** Antigravity (Gemini 3.5 Flash)

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

> severity blindness

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> Priority must be Urgent if description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — every row containing injury, child, school, hospital, fell, or hazard was correctly classified as Urgent.

**Your git commit message for UC-0A:**

> `UC-0A Fix severity blindness and taxonomy drift: Naive prompt would choose inconsistent category names and miss injury/school/child priority overrides → Implemented exact schema mappings, keyword-based severity triggers, and NEEDS_REVIEW flags in classifier.py`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (dual approval from Department Head and HR Director was softened to general approval) and Clause 2.7 (first quarter deadline dropped).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added standard office language and general assumptions like "employees are typically expected to" which are not in the source document.

**Your git commit message for UC-0B:**

> `UC-0B Fix clause omission and obligation softening: Naive summary would miss conditions (such as HR Director + Department Head approvals) or soften binding verbs → Implemented structured parser, exact mapping checks, and verbatim quotation flagging in app.py`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> A single aggregated number for growth across all wards and categories, choosing MoM or YoY silently, and dropping/ignoring the 5 null actual spend values.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards/categories combined. It did not mention the 5 null rows and silently ignored/zeroed them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — the following 5 rows are flagged (returning `NULL - {reason}` for growth and `n/a` for formula, and the subsequent rows depending on them are flagged as `NULL - Previous spend at {period} is null`):
> - Line 58: 2024-03 · Ward 2 – Shivajinagar · Drainage & Flooding (Notes: 'Data not submitted by ward office')
> - Line 124: 2024-05 · Ward 5 – Hadapsar · Streetlight Maintenance (Notes: 'Equipment procurement delay')
> - Line 167: 2024-07 · Ward 4 – Warje · Roads & Pothole Repair (Notes: 'Audit freeze — figures under review')
> - Line 191: 2024-08 · Ward 3 – Kothrud · Parks & Greening (Notes: 'Project suspended — pending approval')
> - Line 255: 2024-11 · Ward 1 – Kasba · Waste Management (Notes: 'Contractor change — billing delayed')

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> `UC-0C Fix naive aggregation and silent null handling: Naive prompt would aggregate all wards, drop null notes, and guess growth type → Implemented strict CLI verification, notes propagation, and MoM/YoY growth computation in app.py`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It stated that personal phones can be used to access approved remote work tools and email, blending IT section 3.1 with HR remote work policies.

**Did it blend the IT and HR policies?**

> Yes — it blended IT device usage rules with HR WFH tools.

**After your fix — what does your system return for this question?**

> Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data. (Source: policy_it_acceptable_use.txt, Sections 3.1 and 3.2)

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> `UC-X Fix cross-document blending and hedged hallucination: Naive prompts would blend IT and HR devices/leave rules, use hedging words, or fail to follow template on refusal → Implemented strict single-source retrieval and exact matching with refusal template formatting in app.py`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Designing precise and complete agents.md files (RICE prompt refinement) was the most challenging step because we had to manually foresee all edge cases, negative boundaries, and ensure that our code validation aligned 100% with these rules.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The dual approval requirement in UC-0B Clause 5.2 ("LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient") and the specific list of severity words in UC-0A.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Standardizing and auditing data exports from municipal database pipelines, making sure strict aggregation policies and PII redaction rules are enforced.

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

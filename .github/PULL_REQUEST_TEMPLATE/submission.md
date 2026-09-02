# Vibe Coding Workshop — Submission PR

**Name:** Nisha Maurya  
**City / Group:** Lucknow  
**Date:** 03 September 2026  
**AI tool(s) used:** Antigravity IDE (Gemini 3.7 Flash)  

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

> Severity blindness (and taxonomy drift) — complaints with urgent safety keywords like school children or electrical hazards were initially classified as Standard priority.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> `"Severity Trigger Enforcement: priority MUST be set to 'Urgent' if the description or location contains ANY of the following severity keywords (case-insensitive): 'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse'. If none are present, assign 'Standard' or 'Low'."`

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing severity triggers (e.g. PM-202402 [children], PM-202411 [hazard], PM-202420 [injury], PM-202446 [fell]) deterministically returned Urgent.

**Your git commit message for UC-0A:**

> `[UC-0A] Fix severity blindness: missing keywords in enforcement → added triggers and complete RICE taxonomy`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and obligation softening — the naive model dropped the secondary approver condition in Clause 5.2 and softened binding verbs ("must" to "should").

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> - Clause 5.2: Dropped HR Director approval (only mentioned Department Head approval).
> - Clause 2.4: Dropped the explicit invalidation of verbal approval.
> - Clause 7.2: Softened the absolute prohibition on leave encashment during active service.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) plus sections 1 through 8 are completely present and legally faithful.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — the naive prompt added generic phrases like "as per standard corporate practice" and "employees are generally encouraged", which were not in the policy text.

**Your git commit message for UC-0B:**

> `[UC-0B] Fix clause omission: completeness not enforced → added every-numbered-clause rule and dual-approver preservation`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated overall growth percentage across all wards and categories combined, without specifying whether it used MoM or YoY.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards blindly and silently ignored/omitted the 5 null actual_spend rows without any warning or audit trail.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — attempting all-ward or cross-category aggregation triggers an explicit REFUSAL error enforcing granular series calculations.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 null rows are audited and flagged with status `NULL_VALUE`:
> 1. 2024-03 · Ward 2 – Shivajinagar · Drainage & Flooding
> 2. 2024-05 · Ward 5 – Hadapsar · Streetlight Maintenance
> 3. 2024-07 · Ward 4 – Warje · Roads & Pothole Repair
> 4. 2024-08 · Ward 3 – Kothrud · Parks & Greening
> 5. 2024-11 · Ward 1 – Kasba · Waste Management

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — 2024-07 is exactly `+33.1%` (monsoon spike) and 2024-10 is exactly `−34.8%` (post-monsoon).

**Your git commit message for UC-0C:**

> `[UC-0C] Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only and added null audit`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, personal phones can be used for approved remote work tools and accessing work email when working from home."

**Did it blend the IT and HR policies?**

> Yes — it improperly blended IT policy Section 3.1 with HR remote working tools, granting unauthorized permissions to access work files on personal devices.

**After your fix — what does your system return for this question?**

> "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data or general work files. Employees using personal devices for CMC email must enable device-level PIN or biometric lock." (Source: policy_it_acceptable_use.txt Section 3)

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — all hedging phrases were completely eliminated through strict single-source attribution rules and standard refusal templates.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all 7 questions produced exact single-source citations or the standard refusal template without exception.

**Your git commit message for UC-X:**

> `[UC-X] Fix cross-doc blending: no single-source rule → added single-source attribution enforcement and refusal template`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The **Analyze** and **Fix** steps were the most critical. Uncovering subtle failure modes (such as silent condition drops like dual-approvers or cross-document policy hallucinations) required careful comparison against ground-truth policy documents and rigorous rule crafting in `agents.md`.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The multi-approver constraint in UC-0B (`"Clause 5.2 explicitly requires approval from BOTH Department Head AND HR Director; manager approval alone is not sufficient"`) and the deterministic refusal template in UC-X.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating policy compliance checking and structured data validation for municipal grievance workflows and operational audit reporting.

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

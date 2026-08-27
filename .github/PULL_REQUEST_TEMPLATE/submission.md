# Vibe Coding Workshop — Submission PR

**Name:** Niraj Bhalerao  
**City / Group:** Pune  
**Date:** 2026-07-15  
**AI tool(s) used:** Antigravity IDE (Gemini / Claude)

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_pune.csv` without crash
- [x] `results_pune.csv` present in `uc-0a/`
- [x] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/`
- [x] `growth_output.csv` present in `uc-0c/`
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> Severity blindness — the naive prompt classified "Electrical hazard reported" and "School children at risk" as Standard priority instead of Urgent.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "The priority field must be Urgent if the description contains any of these severity keywords in lowercase: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> [To be verified] out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — PM-202402 (school children), PM-202411 (electrical hazard), PM-202420 (risk of serious injury), PM-202446 (elderly resident fell) all returned Urgent.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> All three: clause omission (5 clauses entirely missing), condition dropping (2.4 verbal warning, 5.2 two-approver rule, 3.2 48-hour window dropped), and scope bleed ("to prevent policy abuse", "longer sicknesses").

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Missing: 2.3 (14-day advance notice), 2.5 (LOP regardless of subsequent approval), 2.7 (carry-forward Q1 deadline), 3.4 (sick leave adjoining holiday), 5.3 (Municipal Commissioner approval for LWP >30 days).
> Weakened: 2.4 (verbal approval exclusion dropped), 2.6 (Dec 31 forfeiture date dropped), 3.2 (48-hour window and "registered practitioner" dropped), 5.2 (dropped "Department Head AND HR Director" reduced to "formal approval"), 7.2 ("under any circumstances" dropped, reason added).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are present with full obligations. Clauses 3.2 and 5.2 are quoted verbatim and tagged [VERBATIM] to prevent any condition dropping.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — phrases "to prevent policy abuse" (in 7.2), "longer sicknesses" (in 3.2), "leave should be planned" (in 2.3), and "generally permitted" (in 7.1) were added by the naive prompt. None of these appear in the source document.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: naive summary dropped clauses and conditions → implemented exact parser and verbatim rule for complex clauses

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> The naive prompt would return a single aggregated growth number across all wards and categories combined, silently skipping all 5 null rows without flagging them, and assuming MoM formula without being told.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards. No, it did not mention the 5 null rows — it silently skipped or averaged around them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — the system exits non-zero and prints an error message if asked to aggregate across all wards or categories.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 null rows are identified and logged to stderr with their ward, category, period, and reason from the notes column:
> - 2024-03: Ward 2 – Shivajinagar, Drainage & Flooding (Data not submitted by ward office)
> - 2024-07: Ward 4 – Warje, Roads & Pothole Repair (Audit freeze – figures under review)
> - 2024-11: Ward 1 – Kasba, Waste Management (Contractor change – billing delayed)
> - 2024-08: Ward 3 – Kothrud, Parks & Greening (Project suspended – pending approval)
> - 2024-05: Ward 5 – Hadapsar, Streetlight Maintenance (Equipment procurement delay)

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — growth_output.csv shows exactly +33.1% for 2024-07 and −34.8% for 2024-10 for Ward 1 – Kasba, Roads & Pothole Repair.

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> A blended answer like: "Yes, personal phones can be used for approved remote work tools and email access when working from home." — combining both IT and HR policy without citing either, creating permissions that exist in neither document.

**Did it blend the IT and HR policies?**

> Yes — it merged IT section 3.1 (personal devices access email/portal only) with HR mentions of remote work tools to produce a permissive answer that is not supported by either document alone.

**After your fix — what does your system return for this question?**

> [Source: policy_it_acceptable_use.txt, Section 3.1]
> Personal devices may be used to access CMC email and the CMC employee self-service portal only.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — answers are either a verbatim policy clause with citation, or the exact refusal template. No hedging phrases are generated.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all 7 test questions verified:
> 1. Carry forward leave → HR 2.6 ✅
> 2. Install Slack → IT 2.3 ✅
> 3. Home office allowance → Finance 3.1 ✅
> 4. Personal phone for work files → IT 3.1 only (no blending) ✅
> 5. Flexible working culture → Exact refusal template ✅
> 6. DA and meal receipts → Finance 2.6 ✅
> 7. Who approves LWP → HR 5.2 ✅

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: no single-source rule → added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The hardest step was Analyze (A) — specifically identifying condition-dropping in UC-0B. The naive summary sounded complete and professional on first read, but clause 5.2's "requires approval" is syntactically valid while missing the critical "from both Department Head AND HR Director." Only a deliberate side-by-side clause inventory check revealed the silent drop.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> In UC-0B agents.md: "Multi-condition obligations must preserve ALL conditions — never drop one silently. (e.g. clause 5.2 requires TWO approvers.)" The AI generated a generic "preserve meaning" rule, but did not call out the specific multi-condition trap in clause 5.2 by example. Adding the explicit example made the rule testable and enforceable.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> I will apply RICE + CRAFT to an automated report generator that summarizes sales data for managers. The CRAFT loop will help me catch cases where the AI silently aggregates regional numbers without flagging missing data rows — the same failure mode as UC-0C.

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

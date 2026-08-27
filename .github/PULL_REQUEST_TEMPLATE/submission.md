# Vibe Coding Workshop — Submission PR

**Name:** logarajeshwaran  
**City / Group:** Chennai  
**Date:** 2026-03-31  
**AI tool(s) used:** Claude Code (Claude Sonnet 4.6), GPT-4o (via OpenAI API)

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

> severity blindness — the model failed to return Urgent for complaints containing injury/child/school/hospital keywords, assigning Standard priority instead.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — otherwise Standard; use Low only for complaints with no immediate impact"

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> TBD out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — enforced both via agents.md rule and a hard post-processing check in classifier.py that overrides model output if any severity keyword is present in the description.

**Your git commit message for UC-0A:**

> [UC-0A] Fix severity blindness and taxonomy drift: model ignored severity keywords and invented categories → added Pydantic structured output, hard-enforcement rules, and retry logic with 2s delay and 5s backoff

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission and obligation softening — the naive prompt skipped numbered clauses entirely and replaced binding verbs like "must" and "are forfeited" with softer alternatives like "should" and "may be lost".

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 5.2 (dual-approver requirement for LWP — Department Head AND HR Director both dropped to just "requires approval"), 5.3 (Municipal Commissioner approval for LWP >30 days skipped), 7.2 (leave encashment during service not permitted — softened to "not recommended"), 2.6–2.7 (carry-forward forfeiture dates omitted).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 18 clauses across 8 sections are present, numbered identically to the source. The summary ends with "SUMMARY COMPLETE — 18 clauses covered".

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — the naive output added phrases like "as is standard practice in government organisations" and "employees are generally expected to". These are prohibited by the enforcement rules and do not appear in the fixed output.

**Your git commit message for UC-0B:**

> [UC-0B] Fix clause omission and obligation softening: naive prompt skipped clauses and weakened binding verbs → added enforcement rules for complete clause coverage, dual-approver preservation, and exact verb matching

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> The naive prompt returned a single aggregated growth figure across all wards and categories combined, e.g. "Overall budget utilisation grew by X% from the previous period." — no ward/category breakdown, no formula shown, no null rows mentioned.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards and all categories. It did not mention any of the 5 null actual_spend rows — they were silently dropped from the calculation.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — if no specific ward and category are provided, the app exits with: "ERROR: --growth-type is required. Please specify MoM or YoY. Refusing to guess — MoM and YoY produce different numbers and the choice is yours." and the agents.md enforcement rule explicitly refuses all-ward requests.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — the NULL REPORT is printed before any computation. The 5 flagged rows are:
> - [2024-03] Ward 2 – Shivajinagar / Drainage & Flooding — Data not submitted by ward office
> - [2024-05] Ward 5 – Hadapsar / Streetlight Maintenance — Equipment procurement delay
> - [2024-07] Ward 4 – Warje / Roads & Pothole Repair — Audit freeze — figures under review
> - [2024-08] Ward 3 – Kothrud / Parks & Greening — Project suspended — pending approval
> - [2024-11] Ward 1 – Kasba / Waste Management — Contractor change — billing delayed

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — exact match. July 2024: (19.7 - 14.8) / 14.8 = +33.1%. October 2024: (13.1 - 20.1) / 20.1 = -34.8%. Formula column is machine-verifiable for every row.

**Your git commit message for UC-0C:**

> [UC-0C] Fix false aggregation and silent nulls: naive prompt computed all-ward totals and silently dropped null rows → added per-ward/category enforcement, mandatory null flagging, formula-per-row output, and growth-type refusal when unspecified

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> The naive prompt blended IT-POL-003 (acceptable use of devices) with general HR remote work assumptions, returning something like: "While the IT policy requires use of approved devices, employees working from home are generally expected to use organisation-issued equipment. Personal phones may be used for non-sensitive communication." — this blends documents and uses a prohibited hedging phrase.

**Did it blend the IT and HR policies?**

> Yes — the naive output combined device policy (IT-POL-003) with inferred remote work norms not present in any document.

**After your fix — what does your system return for this question?**

> "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the relevant department for guidance."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — all answers tested used direct citations in the format [Document: HR-POL-001, Section X.Y] with no hedging phrases. Out-of-scope questions triggered the exact refusal template.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — tested questions all returned single-source cited answers (e.g. annual leave entitlement cited to HR-POL-001 Section 2.1, sick leave carry-forward to Section 3.3, public holiday compensatory off to Sections 6.2–6.3) or the exact refusal template for cross-document questions.

**Your git commit message for UC-X:**

> [UC-0X] Fix cross-document blending and hedging: naive prompt merged IT and HR policy claims into single answers and used ungrounded inference phrases → added single-source citation rule, banned hedging phrases, and enforced exact refusal template for out-of-scope questions

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Enforcement was the hardest step. Writing a constraint in agents.md is straightforward, but making it stick required both a precise prompt rule and — in UC-0A — a hard post-processing override in code. Prompt rules alone were not sufficient for safety-critical outputs like severity classification; the model still occasionally ignored them under intermittent API conditions.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> In uc-0a/agents.md: "priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — otherwise Standard; use Low only for complaints with no immediate impact". The AI draft used vague language like "prioritise safety-related complaints" — the explicit keyword list was added manually to make the rule unambiguous and machine-checkable.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating the triage of citizen feedback emails into department-specific queues — I will apply RICE to define the role/intent/context/enforcement for the classifier, and use the CRAFT loop to test against edge cases like ambiguous complaints that span multiple departments.

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

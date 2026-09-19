# Vibe Coding Workshop — Submission PR

**Name:** Battini Sadwik  
**City / Group:** Hyderabad / Solo  
**Date:** 15 September 2026  
**AI tool(s) used:** Strawberry, Python standard library, GitHub

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_hyderabad.csv` without crash
- [x] `results_hyderabad.csv` present in `uc-0a/`
- [x] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/`
- [x] `growth_output.csv` present in `uc-0c/`
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**

> Severity blindness and taxonomy drift: the classifier needed fixed category strings and explicit handling for hospitalised/collapsed variants of the required severity signals.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
>
> "Priority must be Urgent when the description contains injury, child, school, hospital/hospitalised, ambulance, fire, hazard, fell, or collapse/collapsed, case-insensitively; otherwise use Standard unless the description is clearly routine and non-urgent, when Low is allowed."

**How many rows in your results CSV match the answer key?**

> The tutor answer key was not available. The generated output contains 15/15 Hyderabad rows with the required schema.

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes. Hospitalised and collapsed variants are also treated as urgent signals because they occur in the Hyderabad test data.

**Your git commit message for UC-0A:**

> [UC-0A] Fix severity blindness: keyword variants were under-specified → enforced urgent triggers and ambiguity rules

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**

> Clause omission and obligation softening, especially where a rule has multiple approvers or multiple timing conditions.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> The control implementation did not produce a summary. The fix explicitly protects clauses 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2, including both approvers in clause 5.2 and all forfeiture/approval conditions.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes. Clauses 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2 are present with clause references.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> The control implementation did not produce a summary. The fixed summarizer uses only the supplied policy file and adds no outside practice or assumptions.

**Your git commit message for UC-0B:**

> [UC-0B] Fix clause omission: completeness was unenforced → preserved every required obligation and condition

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> The control implementation did not calculate growth. The fixed CLI requires an explicit ward, category, and `MoM` growth type rather than guessing or aggregating.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> The fixed implementation refuses all-ward/all-category requests. `load_dataset` reports all five null rows before computation, including each row's notes; a requested series flags its own null rows rather than skipping them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> The generated output is the requested Ward 1 / Roads & Pothole Repair series, which contains no null actual-spend row. The loader still detects all five dataset nulls, and the calculator flags any null encountered in a selected series with its reason.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes: July is +33.1% and October is -34.8%.

**Your git commit message for UC-0C:**

> [UC-0C] Fix silent aggregation: scope and null rules were missing → enforced one ward/category and visible null flags

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**

> The control implementation did not answer questions. The fixed answer is restricted to the IT policy: personal devices may access CMC email and the employee self-service portal only, and may not access, store, or transmit classified or sensitive CMC data.

**Did it blend the IT and HR policies?**

> No. The fixed answer cites only `policy_it_acceptable_use.txt`, sections 3.1 and 3.2.

**After your fix — what does your system return for this question?**

> Personal devices may be used to access CMC email and the CMC employee self-service portal only. [policy_it_acceptable_use.txt, section 3.1] Personal devices must not be used to access, store, or transmit classified or sensitive CMC data. [policy_it_acceptable_use.txt, section 3.2]

**Did your system use any hedging phrases in any answer?**

> No. Unsupported questions use the exact refusal template.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes. Covered questions return single-source citations; the flexible-working-culture question returns the exact refusal template.

**Your git commit message for UC-X:**

> [UC-X] Fix cross-document blending: source boundaries were missing → enforced single-source citations and refusal wording

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The hardest step was fixing the boundary conditions after testing: severity variants, numbered-clause boundaries, null values, and cross-document ambiguity all required explicit rules rather than generic accuracy language. The final implementations make those boundaries visible in both the code and the agent contracts.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The exact refusal rule for unsupported policy questions: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> I will apply it when validating an AI-assisted project workflow: define the allowed evidence and failure boundaries first, then test the generated implementation against explicit safety and correctness cases before publishing it.

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

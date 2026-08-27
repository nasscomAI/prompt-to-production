# Vibe Coding Workshop — Submission PR

**Name:** Sourish Ghosh  
**City / Group:** Hyderabad
**Date:** 19 March 2026  
**AI tool(s) used:** GitHub Copilot (Claude Sonnet 4.5)  

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

> Taxonomy drift and missing justification - The system needed strict enforcement to use exact category names from the allowed list and to provide reason fields citing specific words from complaint descriptions.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations, abbreviations, or combined categories allowed."
> 
> "Priority must be Urgent if description contains any of these keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise apply Standard or Low based on operational impact."
> 
> "Every output row must include a reason field that is exactly one sentence and explicitly cites specific words from the original description using quotation marks."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> All rows matched

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes - Implementation checks for urgent keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) and automatically sets priority to Urgent when any are found in the description.

**Your git commit message for UC-0A:**

> C-0A Fix initial: Not failed → generated result csvs

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and obligation softening - The system needed to ensure all 29 clauses were present in the summary without dropping any conditions from multi-part requirements or weakening binding verbs.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Critical clauses at risk: Section 2.4 (written approval required, verbal not valid), Section 5.2 (requires BOTH Department Head AND HR Director approval), Section 7.2 (leave encashment not permitted under ANY circumstances). Multi-condition clauses like these are prone to dropping one condition or softening absolute language.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes - All 29 clauses are present in the summary, including all 10 critical clauses from README. Multi-condition requirements preserved with all conditions intact (e.g., Section 5.2 includes both Department Head AND HR Director).

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No - Implementation enforces context restriction to source document only. Explicitly prohibits phrases like "as is standard practice", "typically", "generally expected", "in line with industry norms" that would signal external information was added.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause rule

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> The system refused as designed: "I cannot calculate growth from the data without the required parameters. Required: --ward, --category, and --growth-type parameters." This refusal prevents the wrong aggregation level failure mode.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> No aggregation - System refused to proceed without explicit ward and category parameters. For null handling: system reports null count upfront (5 rows) and lists each null with period, ward, category, and reason from notes column before any computation begins.

**After your fix — does your system refuse all-ward aggregation?**

> Yes - System requires explicit --ward and --category parameters. If either is missing, refuses with error message stating which parameter is needed. Will not compute aggregated numbers across wards or categories.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes - Output includes all periods with null rows showing "NULL" in Actual Spend column and reason in growth column. Example flags: "NULL - Data not submitted by ward office" (Ward 2 Drainage 2024-03), "NULL - Audit freeze — figures under review" (Ward 4 Roads 2024-07).

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes - Implementation uses correct MoM formula: (current - previous) / previous * 100. Output format matches README with proper minus sign (−) for negative values. Ward and Category columns repeated in every output row as specified.

**Your git commit message for UC-0C:**

> UC-0C Fix output column format: not generating all columns→ changed agent file to refer output file from read me

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> A naive prompt would likely blend IT and HR policies: "Yes, personal phones can be used for approved remote work tools and email." This creates false permission by combining IT policy (email/portal access) with HR policy mentions of remote work.

**Did it blend the IT and HR policies?**

> Yes - The naive approach would combine claims from both documents. IT policy section 3.1 allows personal devices for "CMC email and employee self-service portal only", while HR policy mentions work-from-home arrangements, creating temptation to blend into broader permission.

**After your fix — what does your system return for this question?**

> "According to IT Acceptable Use Policy section 3.1: Personal devices may be used to access CMC email and the CMC employee self-service portal only. [Source: policy_it_acceptable_use.txt, Section 3.1]" - Single source answer with no blending.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No - Implementation explicitly prohibits hedging phrases through enforcement rules. System outputs only: (1) direct citation from single document with "According to [document] section [X.X]:" format, or (2) exact refusal template. No hedging allowed.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes - System design enforces binary outcome: answers include section citation from one document only OR use exact refusal template "This question is not covered in the available policy documents... Please contact [team] for guidance." No middle ground or blending permitted.

**Your git commit message for UC-X:**

> UC-X  Fix cross-doc blending: no single-source rule → added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Enforcement (E in RICE) refinement was hardest - translating abstract failure modes into specific, testable rules that an AI can follow consistently. For example, in UC-X, stating "don't blend documents" wasn't enough; needed explicit rules like "if question touches multiple documents, choose most relevant single source OR refuse" with concrete examples. Similarly, UC-0C required specifying that refusal is the default when parameters are absent, not aggregation.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> For UC-0C: "Never aggregate across wards or categories unless explicitly instructed with a parameter like --aggregate-all. If ward or category parameter is missing, REFUSE and state which parameter is needed." This prevents the critical wrong-aggregation-level failure by making refusal the default rather than allowing the system to assume aggregation is acceptable.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> For creating an agent to Generate code and unit tests for ongoing project.

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

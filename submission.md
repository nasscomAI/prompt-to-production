Vibe Coding Workshop — Submission PR
Name: Dr C RAVIKUMAR
City / Group: Vellore, Tamilnadu
Date: September 18, 2026
AI tool(s) used: Codex CLI (GPT-based coding assistant)

Checklist — Complete Before Opening This PR
- [x] agents.md committed for all 4 UCs
- [x] skills.md committed for all 4 UCs
- [x] classifier.py runs on test_[city].csv without crash
- [x] results_[city].csv present in uc-0a/
- [x] app.py for UC-0B, UC-0C, UC-X — all run without crash
- [x] summary_hr_leave.txt present in uc-0b/
- [x] growth_output.csv present in uc-0c/
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

UC-0A — Complaint Classifier
Which failure mode did you encounter first? (taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)
taxonomy drift + false confidence

What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:
"Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No alternative spellings or sub-categories."

How many rows in your results CSV match the answer key? (Tutor will release answer key after session)
TBD after tutor key release out of 15

Did all severity signal rows (injury/child/school/hospital) return Urgent?
Yes — severity-keyword rows were marked Urgent in generated outputs.

Your git commit message for UC-0A:
UC-0A Fix taxonomy drift and false confidence: scaffold + narrow matching caused inconsistent labels and excessive NEEDS_REVIEW -> implemented strict rules in agents/skills, built deterministic classifier, expanded pattern coverage, and reran all city outputs

UC-0B — Summary That Changes Meaning
Which failure mode did you encounter? (clause omission / scope bleed / obligation softening)
clause omission + obligation softening

List any clauses that were missing or weakened in the naive output (before your RICE fix):
5.2 (dual approver condition), 2.4 (written approval before leave), 2.5 (LOP regardless of subsequent approval), 3.4 (certificate regardless of duration), 7.2 (encashment prohibition).

After your fix — are all 10 critical clauses present in summary_hr_leave.txt?
Yes — all 10 critical clauses are present.

Did the naive prompt add any information not in the source document (scope bleed)?
No in final compliant output; naive-run bleed text was not preserved.

Your git commit message for UC-0B:
UC-0B Fix clause omission: preserve all clause conditions, add guardrails, and generate compliant summary

UC-0C — Number That Looks Right
What did the naive prompt return when you ran "Calculate growth from the data."?
Naive run output was not stored verbatim; behavior showed aggregation tendency and incomplete null handling.

Did it aggregate across all wards? Did it mention the 5 null rows?
It tended to aggregate; null-row reporting was incomplete before fixes.

After your fix — does your system refuse all-ward aggregation?
Yes.

Does your growth_output.csv flag the 5 null rows rather than skipping them?
Yes — flagged rows:
- 2024-03 | Ward 2 – Shivajinagar | Drainage & Flooding
- 2024-05 | Ward 5 – Hadapsar | Streetlight Maintenance
- 2024-07 | Ward 4 – Warje | Roads & Pothole Repair
- 2024-08 | Ward 3 – Kothrud | Parks & Greening
- 2024-11 | Ward 1 – Kasba | Waste Management

Does your output match the reference values (Ward 1 Roads +33.1% in July, 34.8% in October)?
July matches at +33.1%; October appears as -34.8% in current MoM output (directional sign preserved).

Your git commit message for UC-0C:
UC-0C Fix aggregation/null errors: enforce ward-category scope, null flags, formulas, and growth output

UC-X — Ask My Documents
What did the naive prompt return for the cross-document test question? (Question: "Can I use my personal phone to access work files when working from home?")
Naive output was not saved verbatim; observed failure risk was cross-document blending.

Did it blend the IT and HR policies?
Yes — that was the key pre-fix failure mode.

After your fix — what does your system return for this question?
"According to policy_it_acceptable_use.txt section 3.1: Personal devices may be used to access CMC email and the CMC employee self-service portal only."

Did your system use any hedging phrases in any answer? ("while not explicitly covered", "typically", "generally understood")
No.

Did all 7 test questions produce either a single-source cited answer or the exact refusal template?
Yes.

Your git commit message for UC-X:
UC-X Fix cross-doc blending: enforce single-source cited answers with exact refusal template

CRAFT Loop Reflection
Which CRAFT step was hardest across all UCs, and why?
Refine was hardest because outputs looked correct initially but still broke strict constraints such as dropped conditions, blended citations, or silent null handling. Converting these into deterministic checks took the most effort.

What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?
"Never combine claims from two different documents into one answer."

Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:
Building an internal policy Q&A workflow where each answer must cite one source section or return a strict refusal template.

Reviewer Notes (tutor fills this section)
Criterion
Score /4
Notes
RICE prompt quality


agents.md quality


skills.md quality


CRAFT loop evidence


Test coverage


Total
/20

Badge decision:
- [ ] Standard badge — meets pass threshold (score 11+/20 on this review, full rubric 22+/40)
- [ ] Distinction badge — meets distinction threshold (score 17+/20 on this review, full rubric 34+/40)
- [ ] Not yet — resubmit after addressing: _______________

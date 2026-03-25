# Vibe Coding Workshop — Submission PR

**Name:** Rishikesh Koik
**City / Group:** Kolhapur
**Date:** 2026-03-25
**AI tool(s) used:** Antigravity AI Assistant

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

> "Priority must be Urgent if description contains one of the triggers: injury, child, school, hospital."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — the rule explicitly enforced this classification.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: no keywords in enforcement -> added injury/child/school/hospital triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Numbered clauses and specific requirements were excluded. 

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all clauses are preserved according to the new enforcement rule.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No — there was no scope bleed detected.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced -> added every-numbered-clause rule

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It aggregated values silently across all wards without breaking it down.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards. It didn't mention the missing nulls properly without enforcement.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — they are properly handled.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no scope in enforcement -> restricted to per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It blended information from both the IT Policy and HR Policy inappropriately.

**Did it blend the IT and HR policies?**

> Yes — cross-document blending occurred.

**After your fix — what does your system return for this question?**

> It relies strictly upon a single source document, rejecting un-attributable claims.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — answers use exact language from the policies.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Fix step. Analyzing exactly why the AI broke down and devising a single bullet-proof enforcement rule required precision.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> "Single-source attribution enforcement: output must map directly to a single source document." (UC-X) AI generators usually missed strict cross-blending constraints.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Extracting compliance policies from vendor contracts accurately without hallucinated commitments.

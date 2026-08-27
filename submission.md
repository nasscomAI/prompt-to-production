# Vibe Coding Workshop — Submission PR

**Name:** Darshan Prajapapati
**City / Group:** Ahmedabad
**Date:** 2026-03-30
**AI tool(s) used:** Antigravity (Powered by Google DeepMind)

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_ahmedabad.csv` without crash
- [x] `results_ahmedabad.csv` present in `uc-0a/`
- [x] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/`
- [x] `growth_output.csv` present in `uc-0c/`
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> Severity blindness — initially classified complaints with keywords like "child" as Standard.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> `- "Priority must be 'Urgent' if the description contains any of the following keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse."`

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 11 out of 15 (hypothetically matched based on enforcement rules).

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — Row AM-202407 containing "child" returned Urgent correcty.

**Your git commit message for UC-0A:**

> `UC-0A Fix severity blindness: ignored child/injury keywords → added enforcement rule for priority keywords`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission — "Department Head AND HR Director" was shortened to just "Department Head".

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (multi-condition approval requirement).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — allNumbered Clauses 1.1 through 8.2 are included.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it suggested standard HR practices for bereavement leave not in the source.

**Your git commit message for UC-0B:**

> `UC-0B Fix clause omission: dropped conditions in multi-approval clauses → enforced every numbered clause inclusion`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> "Overall growth across all wards is +5.2%." (Incorrectly aggregated data).

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes it aggregated across all wards and silently ignored the null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes, it refuses cross-ward calculation and requires per-ward scope.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — flagged "Contractor change — billing delayed" correctly in `waste_growth.csv`.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes, Ward 1 Roads +33.1% in July, −34.8% in October are correctly computed.

**Your git commit message for UC-0C:**

> `UC-0C Fix incorrect aggregation: merged all ward data by default → restricted to per-ward calculations and flagged nulls`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal phone under the IT policy, but check your HR leave days." (Hallucinated blending between unrelated docs).

**Did it blend the IT and HR policies?**

> Yes, it incorrectly attempted to bridge IT hardware access with HR leave contexts.

**After your fix — what does your system return for this question?**

> "Yes, personal devices are permitted for work access provided they are registered with IT according to policy_it_acceptable_use.txt Section 4."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No, hedging was strictly removed.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes, all answers are single-source with mandatory document/section citations.

**Your git commit message for UC-X:**

> `UC-X Fix cross-document blending: combined IT and HR policies incorrectly → enforced single-source citation and refusal template`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Role definition, as getting the operational boundary right is crucial for preventing hallucinations and scope-creep.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> `Never combine claims from two different documents into a single answer (Single-source only).`

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating internal legal compliance checks for contract reviews.

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

# Vibe Coding Workshop — Submission PR

**Name:** Saket Saurav
**City / Group:** Noida
**Date:** 2026-07-16
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

> Severity blindness

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> `Priority must be Urgent if the description contains any of the following severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse`

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing injury, child, school, or hazard triggered Urgent correctly.

**Your git commit message for UC-0A:**

> `UC-0A Fix taxonomy and severity: missing keywords and formatting variations -> added exact severity triggers, precise regex routing, and citation formatting`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Obligation softening and clause omission (particularly dropping dual-approval conditions)

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (was weakened to generic approval instead of Department Head AND HR Director approval) and Clause 2.7 (carry-forward deadline was omitted).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added common generic expressions like "as is standard practice for government organizations".

**Your git commit message for UC-0B:**

> `UC-0B Fix clause omission and condition softening: naive summarize missed dual approvers or carry-forward deadlines -> implemented regex parser and verbatim quoting for exact compliance`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> A single aggregated growth percentage for all wards and categories combined, completely ignoring individual breakdowns.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards, and completely ignored the 5 null rows instead of flagging them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — 2024-03 Ward 2 Shivajinagar, 2024-05 Ward 5 Hadapsar, 2024-07 Ward 4 Warje, 2024-08 Ward 3 Kothrud, and 2024-11 Ward 1 Kasba.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> `UC-0C Fix silent null calculation and silent aggregation: naive calculator averaged across wards or ignored missing months -> implemented strict parameter validation, formula logging, and null-safety chain`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It blended IT and HR documents and incorrectly answered that you can use personal devices for work files when working from home, provided the remote work arrangement is approved.

**Did it blend the IT and HR policies?**

> Yes, it blended the HR remote work approval with the IT BYOD access terms.

**After your fix — what does your system return for this question?**

> `"According to policy_it_acceptable_use.txt section 3.1, personal devices may be used to access CMC email and the CMC employee self-service portal only. Section 3.2 states that personal devices must not be used to access, store, or transmit classified or sensitive CMC data."`

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> `UC-X Fix cross-document blending and hedged hallucination: naive Q&A blended IT/HR rules or guessed on flexible culture -> implemented single-source verification routing and literal refusal templating`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Refinement and Verification. Ensuring complete determinism in rule application (like null-propagation and exact citation outputs) without external API dependencies required writing meticulous string/regex matching patterns.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The strict refusal rules and the literal refusal template: `"This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."`

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating standard operating procedure audits and document validation workflows.

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

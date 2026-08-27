# Vibe Coding Workshop — Submission PR

**Name:** Kaushal B
**City / Group:** Bangalore
**Date:** March 24, 2026
**AI tool(s) used:** Antigravity (Google Deepmind)

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

> taxonomy drift

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — the rule explicitly looked for those trigger words.

**Your git commit message for UC-0A:**

> UC-0A Fix taxonomy drift: categories hallucinated -> restricted output to exact string list and added severity triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> condition dropping / obligation softening

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 was weakened by dropping the HR Director approval requirement, keeping only the Department Head. Clause 7.2 was softened.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added phrases like "as is standard practice for most organisations".

**Your git commit message for UC-0B:**

> UC-0B Fix condition dropping: dual approvals lost -> enforced all multi-condition obligations must be preserved exactly

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> "Overall budget growth across all wards is 15.2%."

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated all wards indiscriminately and silently skipped the 5 null rows without any warning.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — they are flagged as "NULL DATA" drawing directly from the notes column.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix silent null handling: nulls ignored -> enforced explicit flagging of null rows and disabled multi-ward aggregation

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, personal phones can be used for approved remote work tools and email."

**Did it blend the IT and HR policies?**

> Yes — it improperly blended the HR remote tool allowance with the IT self-service portal restrictions to fabricate permission.

**After your fix — what does your system return for this question?**

> "[policy_it_acceptable_use.txt, Section 3.1] Personal devices may access CMC email and the employee self-service portal only."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: merged answers from varying docs -> enforced strict single-source citation or exact verbatim refusal template

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The 'T' (Test) step was the hardest. Spotting missing conditions (like the second approver in UC-0B) required slow, meticulous visual inspection of the output against the ground truth.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> "If a question is not directly and fully answered by a single document, you must output exactly: 'This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.' with no other text."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> I will apply RICE + CRAFT to build internal team onboarding documentation chatbots to completely stop them from hallucinating standard HR answers over our specific team engineering policies.

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

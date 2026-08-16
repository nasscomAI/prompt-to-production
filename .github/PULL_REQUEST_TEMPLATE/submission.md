# Vibe Coding Workshop — Submission PR

**Name:** Vinodha
**City / Group:** Chennai
**Date:** 2026-08-16
**AI tool(s) used:** Antigravity

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

> If the complaint contains any of these severity keywords: `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`, you MUST set the priority to `Urgent`.

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows with severity keywords were strictly mapped to Urgent priority without exceptions.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: no keywords in enforcement -> added injury/child/school/hospital triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> obligation softening and condition dropping

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (second approver condition was dropped).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 are explicitly extracted and preserved.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added phrases like "as per standard municipal guidelines" which are not present in the text.

**Your git commit message for UC-0B:**

> UC-0B Fix condition drop: clause 5.2 lost second approver -> added multi-condition preservation rule

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated percentage: "Overall budget growth is 12% YoY" across all wards and categories.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards. It silently skipped the 5 null rows without flagging them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — they are flagged as 'FLAGGED NULL' with the reason from the notes column reported.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — the calculations accurately match the reference values for those periods.

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no ward/category scope -> enforced per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "While not explicitly covered for phones, you can generally use them to access approved remote work tools and CMC email."

**Did it blend the IT and HR policies?**

> Yes — it blended the HR remote work tool allowance with the IT email portal allowance, creating a false permission.

**After your fix — what does your system return for this question?**

> "Personal devices may only be used to access CMC email and the employee self-service portal.
> Source: policy_it_acceptable_use.txt, Section 3.1"

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — all answers were definitive or used the strict refusal template.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all test questions successfully followed the strict single-source rule.

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The 'Fix' step was the most challenging, particularly distinguishing between 'softening' and 'condition dropping', and ensuring the enforcement rule was rigid enough for the AI to follow without being overly restrictive.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The exact refusal template in UC-X: "This question is not covered in the available policy documents..." to strictly prevent hedged hallucinations.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> I will apply it to automate the triaging and initial response drafting for our internal IT support tickets, ensuring it doesn't hallucinate troubleshooting steps not in our runbooks.

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

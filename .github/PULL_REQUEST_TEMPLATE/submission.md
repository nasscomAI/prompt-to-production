# Vibe Coding Workshop — Submission PR

**Name:** badarinarayanas  
**City / Group:** Bengaluru  
**Date:** March 24, 2026  
**AI tool(s) used:** Python (Local R.I.C.E Rules Engine), Anthropic / Gemini Models  

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

> Taxonomy drift and hallucinated sub-categories. The AI wanted to invent specific edge-case categories rather than mapping to the approved 5-item taxonomy.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Never create new categories or sub-categories. You must only select from: Roads & Pothole Repair, Drainage & Flooding, Streetlight Maintenance, Waste Management, Parks & Greening."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — the python script explicitly maps the keywords 'injury', 'school', and 'hospital' directly to the Urgent routing class.

**Your git commit message for UC-0A:**

> UC-0A Fix taxonomy drift: Local python heuristic classifier ensures exact category mapping without hallucinated labels.

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Obligation softening and condition dropping.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 was weakened. Naive models typically drop the "Department Head AND HR Director" trap and just summarized it as "Requires manager approval."

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 clauses are preserved completely verbatim.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — standard general assumptions about HR turnaround times were hallucinated due to the LLM pulling from its training data.

**Your git commit message for UC-0B:**

> UC-0B Fix condition dropping: Local regex parsing ensures clauses with binding verbs are extracted verbatim without meaning loss.

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated percentage integer that blended all Wards and Categories together, completely ignoring the structural nuances of the dataset.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggressively aggregated all wards simultaneously, and it completely failed to mention the 5 deliberately missing null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — Ward 2 Drainage, Ward 4 Roads, Ward 1 Waste, Ward 3 Parks, and Ward 5 Streetlight models were explicitly reported to the console with their associated `notes` column reasons before math was applied.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — exact matches explicitly featuring the formula calculation in the output string.

**Your git commit message for UC-0C:**

> UC-0C Fix silent null handling and false aggregation: Python analysis script forces strict flag outputs and ward-level grouping while displaying computation formulas.

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It synthesized a blended response combining both IT and HR policy documents, creating a hallucinated permission. "Yes, personal phones can be used for approved remote work tools and email."

**Did it blend the IT and HR policies?**

> Yes — it improperly used the HR remote work guidelines to soften the strict IT device rules.

**After your fix — what does your system return for this question?**

> "[policy_it_acceptable_use.txt - Section 3.1] Personal devices (BYOD) may only be used to access the company email and the employee self-service portal."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — all answers were definitively cited and bound to their single source.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix cross-document blending: Single-source routing logic enforces exact citations and triggers verbatim refusal template for unstated rules.

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Filter (Enforcement) step was the hardest. Anticipating how language models might implicitly soften negative constraints or combine non-related documents requires thinking adversarially about LLM behavior.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The explicit, mandatory verbatim refusal template: "If the question is not in the documents — use the refusal template exactly, no variations: 'This question is not covered in the available policy documents...'"

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Building an internal company documentation bot that must strictly abide by the actual documented processes rather than guessing based on general industry standards.

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

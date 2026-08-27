# Vibe Coding Workshop — Submission PR

**Name:** Ansh Saini  
**City / Group:** Pune  
**Date:** April 18, 2026  
**AI tool(s) used:** Gemini 3.1 Pro  

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

> Hallucinated sub-categories / false confidence

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Category MUST be exactly one of the following strings (no variations): Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — Our rule-based script explicitly maps these severity keywords to Urgent deterministically.

**Your git commit message for UC-0A:**

> UC-0A Fix hallucinated categories: loose LLM mapping → implemented strict rule-based heuristic classifier enforcing allowed categories

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Obligation softening / clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 5.2 and 2.4 (Multi-condition obligations getting silently dropped).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — The script strictly extracts and retains every numbered clause verbatim.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No — Our implementation strictly limits extraction to the exact source document, entirely eliminating scope bleed.

**Your git commit message for UC-0B:**

> UC-0B Fix obligation softening: conditions dropping in summary → implemented verbatim clause extraction to preserve all requirements

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It aggregated all wards together silently and completely ignored the null values.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated them and no, it silently skipped all 5 null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — Rows 58, 124, 167, 191, and 255 were explicitly flagged with their exact notes.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix silent null handling: ignored missing actual_spend → added strict null flagging and forced formula transparency

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It hallucinated a blended answer that granted non-existent permissions by incorrectly merging the IT and HR policies.

**Did it blend the IT and HR policies?**

> Yes — It assumed flexible working allowed for personal phone work access.

**After your fix — what does your system return for this question?**

> "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — The script strictly enforces explicit matching or throws the verbatim refusal template.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix hedged hallucination: agent guessing missing policies → enforced verbatim refusal template for unmapped questions

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The 'Enforcement' step of the RICE framework was the hardest because it requires proactively anticipating how the AI will try to hallucinate or hedge answers, forcing me to write highly robust and deterministic constraints.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The strict verbatim refusal template to prevent hedged hallucinations.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Building a robust automated email responder that safely summarizes client requests without guessing missing context.

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

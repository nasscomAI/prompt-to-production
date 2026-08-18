# Vibe Coding Workshop — Submission PR

**Name: Janaki Ram Kolluru**  
**City: Hyderabad**  
**Date: 14-03-2026**  
**AI tools used: Gemini 3.1, Claude Sonnet 4.6, ChatGPT 5.3**  

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
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> Taxonomy drift

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations or hallucinated sub-categories are allowed."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — explicit keyword matching was built into the classifier logic to guarantee Urgent priority when these signals appeared.

**Your git commit message for UC-0A:**

> UC-0A Fix [Taxonomy drift · Severity blindness · Missing justification · False confidence]: stub → classifier with exact category schema, severity-keyword Urgent, reason citation, NEEDS_REVIEW flag

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and scope bleed.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (dual-approver requirement weakened) and 7.2 (strict prohibition on encashment softened).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — the application explicitly checks the 10 critical clauses against a hardcoded list and raises an omission warning if any are missing.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — standard HR phrases like "typically in government organisations" appeared previously, which have now been eliminated by enforcing rule-based summarisation.

**Your git commit message for UC-0B:**

> UC-0B Fix [Clause omission · Obligation softening · Scope bleed]: stub → clause-faithful summariser, verbatim high-risk clauses, omission guard, no external content

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated percentage for the entire dataset, completely obscuring per-ward category dynamics.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated all wards into one number, and it silently interpolated or skipped the 5 null rows without flagging them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 rows are explicitly flagged as NULL_FLAGGED accompanied by the null reason extracted from the notes column.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix [Wrong aggregation level · Silent null handling · Formula assumption]: stub → per-ward/category calculator, null flags with reasons, formula display, growth-type refusal

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It falsely blended HR equipment language with IT BYOD permissions, stating personal phones could be used for approved remote work instead of strictly limiting it to email and the self-service portal per IT limits.

**Did it blend the IT and HR policies?**

> Yes — it improperly synthesised conditions from different domains.

**After your fix — what does your system return for this question?**

> It returns the exact clause from the IT policy (Section 3.1) regarding personal device usage, explicitly citing it, without blending into HR policy text.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — if a topic wasn't covered, it output the strict refusal template.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix [Cross-document blending · Hedged hallucination · Condition dropping]: stub → single-source Q&A, section citations, per-doc separation, verbatim refusal template

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Refining the enforcement rules during the Feedback step was the hardest. Understanding exactly what condition the AI was dropping or softening required carefully comparing the outputs to the base context.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> "Never combine claims from two different policy documents into a single answer sentence. If a question touches two documents, answer each document's scope separately with separate citations, and do not synthesise them into a joint permission or conclusion."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Reviewing and extracting financial data from unstructured vendor contracts into categorized database rows.

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

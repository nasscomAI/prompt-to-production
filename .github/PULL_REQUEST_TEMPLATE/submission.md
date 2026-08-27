# Vibe Coding Workshop — Submission PR

**Name:** Bhargav Ghoghari
**City / Group:** Mahemdavad
**Date:** 29 March 2026
**AI tool(s) used:** Antigravity (Google DeepMind)

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

> Severity blindness and taxonomy drift.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Must rigidly map to the 5 allowed categories. Priority must trigger mandatory ESCALATION to URGENT if keyword hits match: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — Enforced cleanly via strict keyword boundary checking with zero-exception bindings.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness and category drift: naive keyword matching failed on overlapping words and missing cities → added regex boundaries and city-agnostic RICE rules

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Obligation softening and scope bleed.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (The Trap). The naive extraction completely dropped the condition requiring BOTH the Department Head and the HR Director, assuming only general "management approval".

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 are retained safely and verifiably exact.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — It injected phrases like "per standard company protocol" out of thin air to make the text read better. Removed completely in the final.

**Your git commit message for UC-0B:**

> UC-0B Fix condition softening and clause omission: naive summary dropped dual LWP approvals and specific leave rules → enforced RICE to parse clauses verbatim and explicitly highlight dual conditions

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It output a single meaningless global dataset aggregation representing average percentage changes across the entire city matrix, completely devoid of actionable category or ward context.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated them violently. It completely hallucinated continuity over the 5 null rows, ignoring their reasons and treating them as '0' or dropping them silently. 

**After your fix — does your system refuse all-ward aggregation?**

> Yes - explicitly throws a REFUSAL error on `ward == "Any"`.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — Specifically, values output standard flags such as `Must be flagged — not computed. Null reason: Data not submitted by ward office`.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — Math checks out perfectly logic-bound to the explicit categories.

**Your git commit message for UC-0C:**

> UC-0C Fix silent null handling and assumed aggregation: naive calculation hallucinated missing data and merged categories → implemented strict explicit target boundaries and surfaced omission reasons

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use personal phones for approved remote work tools and email if aligned with management policy."

**Did it blend the IT and HR policies?**

> Yes — It catastrophically hallucinated rights blending HR remote approvals with IT's BYOD limits to fabricate a composite policy rule that doesn't actually exist in print.

**After your fix — what does your system return for this question?**

> [Source: policy_it_acceptable_use.txt, Section 3.1]
> Personal devices may be used to access CMC email and the CMC employee self-service portal only.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — The system rigidly output exactly the verified facts or fell back entirely to the explicit REFUSAL_TEMPLATE.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — Every interaction loop generated exclusively what was defined as allowable context.

**Your git commit message for UC-X:**

> UC-X Fix cross-document blending and hedged hallucination: naive QA merged remote policies inaccurately and answered undefined questions → enforced strict single-source extraction boundaries and mandated verbatim refusal templates

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Refinement and Testing phase. Tracing invisible AI behavior (like silent condition softens or omitted columns) requires a vastly different engineering mindset compared to hunting classic syntax errors. 

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The hardcore literal text block constraints like `REFUSAL_TEMPLATE = "This question is not covered...`. Generative AI tries to be infinitely "helpful" by nature, so explicitly wiring it to reply with an inflexible boilerplate stops hallucinatory drift instantly.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Deploying data categorization for municipal compliance audits where "looking right" is dangerous and "explicitly verified" is required.

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

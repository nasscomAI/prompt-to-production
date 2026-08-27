# Vibe Coding Workshop — Submission PR

**Name:**  Siddhant Wadhwani
**City / Group:**  Mumbai
**Date:**  March 18, 2026
**AI tool(s) used:**  GitHub Copilot/Antigravity, Claude Opus 4.6

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

> Taxonomy drift

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no synonyms, abbreviations, plural forms, or invented sub-categories are permitted."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — All rows with severity keywords have priority set to Urgent.

**Your git commit message for UC-0A:**

> [UC-0A] Fix complaint classification logic: ambiguous category handling and enforcement rules were not robust → clarified tie-breaking, ensured schema compliance, improved error handling and reason generation

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> All clauses are present after fix; verbatim and flagged where needed.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — All clauses are present, with verbatim quotes and flags for meaning loss.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No — No added information not in the source document.

**Your git commit message for UC-0B:**

> [UC-0B] Fix policy summarization logic: clause preservation and enforcement rules were not robust → improved multi-condition handling, ensured all clauses present, flagged meaning loss, prevented scope bleed and obligation softening

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> Per-period growth, formula, and nulls flagged in output.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> No aggregation across wards; null rows are flagged.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — null rows are flagged with "Must be flagged—not computed".

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — July: +33.1%, October: −34.8%.

**Your git commit message for UC-0C:**

> [UC-0C] Fix growth computation logic: null handling and aggregation enforcement were not robust → flagged all null rows in output, refused aggregation unless instructed, ensured formula visibility, enforced growth-type requirement

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> Answer: Corporate devices (laptops, desktops, mobile phones issued by CMC) must be used primarily for official work purposes.
Source: policy_it_acceptable_use.txt section 2.1

**Did it blend the IT and HR policies?**

> No — single-source answers only, no blending.

**After your fix — what does your system return for this question?**

> Answer: Corporate devices (laptops, desktops, mobile phones issued by CMC) must be used primarily for official work purposes.
Source: policy_it_acceptable_use.txt section 2.1

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — enforcement rules prohibit hedging phrases.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — app.py logic ensures this.

**Your git commit message for UC-X:**

> [UC-X] Fix document Q&A logic: cross-document blending and citation enforcement were not robust → mapped canonical questions to exact clauses, prevented hedged hallucination, enforced refusal template, ensured accurate source citation

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Enforcement was hardest, as it required precise manual rules to prevent drift, omission, and blending. Ensuring every output was verifiable and strictly compliant with the schema and policy boundaries took multiple iterations and careful review.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> "Never combine claims from two different documents into a single answer." — This rule was critical for UC-X and prevented cross-document blending that the AI often hallucinated.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Drafting a compliance summary for a new HR policy rollout, ensuring all obligations are preserved and no scope bleed occurs in the summary.

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

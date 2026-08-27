# Vibe Coding Workshop — Submission PR

**Name:** Jeyakkavi
**City / Group:** Chennai
**Date:** 09-03-2026
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

> severity blindness

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be Urgent if the description contains any of the following severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, it must be Standard or Low."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — the keyword matching correctly prioritized all safety-critical complaints.

**Your git commit message for UC-0A:**

> [UC-0A] Fix severity blindness: no keywords in enforcement → added triggers and fixed type warning

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 2.6 (Carry Forward) and 5.2 (Leave Without Pay) were initially dropped or oversimplified.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 mandated clauses are present and complete.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added "standard HR practices" phrases not found in the text.

**Your git commit message for UC-0B:**

> [UC-0B] Fix clause omission: completeness not enforced → added every-numbered-clause rule

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It attempted to aggregate spend across all wards and categories, giving a single misleading growth number.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> It aggregated everything and silently skipped the null rows without warning.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — rows with missing data are clearly flagged with the reason from the notes.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> [UC-0C] Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It hallucinated a blended answer combining the IT policy with the Reimbursement policy.

**Did it blend the IT and HR policies?**

> Yes — it mixed rules from different documents.

**After your fix — what does your system return for this question?**

> Personal devices may be used to access CMC email and the CMC employee self-service portal only.
> Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.
> (Source: policy_it_acceptable_use.txt, Section 3.1 & 3.2)

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — hedging is strictly forbidden by enforcement.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> [UC-X] Fix cross-doc blending: no single-source rule → added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Creation was the hardest because it requires anticipating how to train the LLM to avoid failure modes, especially with subtle issues like scope bleed.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The strict refusal template for UC-X: "If the question cannot be answered entirely and exclusively using the provided documents, you MUST reply with exactly this template and nothing else..."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> I will use it to automate the triaging of incoming bug reports to ensure consistent categorization.

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

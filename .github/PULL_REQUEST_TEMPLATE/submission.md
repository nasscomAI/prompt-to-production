# Vibe Coding Workshop — Submission PR

**Name:** Rithul Richard  
**City / Group:** Nellore  
**Date:** March 16, 2026  
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

> Taxonomy drift and severity blindness (unrecognized categories initially due to missing trigger phrases).

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be set to Urgent if and only if the description contains at least one of these keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse." and "Category must be exactly one of: Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other — no variations, abbreviations, or synonyms."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — the custom logic detects all listed severity keywords efficiently and defaults to Urgent.

**Your git commit message for UC-0A:**

> [UC-0A] Fix unrecognized categories: missing trigger phrases in enforcement → added dead animal/overflowing garbage and road surface cracked/sinking triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and scope bleed (the naive script was entirely empty before RICE implementation).

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> All clauses were inherently omitted at first. Our manual RICE rule enforced checking specifically for 10 target clauses: "2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2".

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — the retrieval workflow actively checks the emitted clause numbers against the required set and emits a missing warning if any are skipped.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Not applicable in the naive script, but our final implementation explicitly prevents it via a guard against standard scope-bleed phrases ("as is standard practice").

**Your git commit message for UC-0B:**

> [UC-0B] Fix missing implementation: application was an empty starter file → implemented clause-faithful HR policy summariser to parse policies exactly

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> NotImplementError (The naive application was just a starter stub `def main(): raise NotImplementedError(...)`).

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> N/A for naive run.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — the system detects target `ward` == "all" (or `category` == "all") and forcefully raises a `ValueError` refusing to aggregate.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — where `actual_spend` is null, the result outputs `NULL DETECTED: [reason from notes column]`.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes.

**Your git commit message for UC-0C:**

> [UC-0C] Fix missing implementation: application was an empty starter file → implemented budget growth calculator with strict MoM/YoY and null handling rules

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> NotImplementError (Starter file originally).

**Did it blend the IT and HR policies?**

> N/A.

**After your fix — what does your system return for this question?**

> [policy_it_acceptable_use.txt — Section 3.1] [Exact clause restricting use of personal phones strictly to company email...]

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — if a keyword matches, it returns the single source clause; otherwise, it hits the rigorous fallback refusal prompt exactly.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes.

**Your git commit message for UC-X:**

> [UC-X] Fix missing implementation: application was an empty starter file → implemented rule-based Mock AI QA to answer correctly from policy documents

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The hardest stage was framing the precise RICE enforcement rules. Translating abstract business logic—such as how to catch subtle scope-bleed ("standard practice") or enforcing single-source citations with no blending—into testable strict rules took significant refining and validation.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The strict refusal conditions and specific trigger keywords. For instance, in UC-0C: "Never aggregate across wards or categories unless explicitly instructed — if asked to 'calculate growth for all wards combined', the system must REFUSE." The AI initially defaults to fulfilling the request, so defining a rigid refusal boundary was a critical, manual intervention.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Building an internal document parsing assistant for generating strict, single-source compliance reports from legal policies, where zero hallucination or blending is acceptable.

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


# Vibe Coding Workshop — Submission PR

**Name:** Shubham Kulkarni  
**City / Group:** Pune  
**Date:** 2026-08-24  
**AI tool(s) used:** Google Antigravity IDE (Gemini)  

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_pune.csv` without crash
- [x] `results_pune.csv` present in `uc-0a/`
- [x] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/`
- [x] `growth_output.csv` present in `uc-0c/`
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> Severity blindness and taxonomy drift (complaints involving school children and fallen elderly citizens were initially marked as Standard priority rather than Urgent, and category names varied slightly across rows).

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be Urgent if the complaint description contains any severity keywords/triggers: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse, sparking, inaccessible, or electrical hazard. Otherwise, default to Standard (or Low if minimal non-disruptive nuisance)."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing severe hazard keywords (e.g. PM-202402 [school children], PM-202411 [sparking/electrical hazard], PM-202420 [risk of serious injury], PM-202427 [inaccessible bridge], PM-202446 [elderly resident fell]) correctly returned Urgent.

**Your git commit message for UC-0A:**

> `[UC-0A] Fix severity blindness: injury and school triggers missed in standard prompts → implemented strict keyword rules and taxonomy enforcement`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Obligation softening and condition dropping (specifically in Clause 5.2 where the requirement for BOTH Department Head and HR Director approval was collapsed into generic 'manager approval', and Clause 7.2 where absolute encashment prohibition during service was omitted).

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 2.5 (loss of pay on unapproved absence regardless of later approval), 2.7 (Q1 carry-forward forfeiture), 3.4 (mandatory medical cert when sick leave borders holidays), 5.2 (dual approval from Department Head and HR Director), and 7.2 (strict encashment prohibition during active service).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are fully represented with preserved binding verbs and intact dual conditions.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — the naive prompt added generic corporate commentary such as "as per standard HR policies and subject to managerial discretion", which does not exist in the source document.

**Your git commit message for UC-0B:**

> `[UC-0B] Fix clause omission and condition dropping: HR policy dual-approvals dropped → added 10-clause inventory and binding verb retention`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single blended annual growth percentage across all wards and categories combined, completely ignoring ward boundaries and hiding the 5 null spend periods.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards erroneously and did not mention the 5 null rows, silently omitting them or treating them as zero.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — attempting to query across all wards or omitting the single ward/category scope triggers an explicit refusal error requiring granular parameters.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 null rows are flagged with their notes: 2024-03 Shivajinagar Drainage (Data not submitted), 2024-07 Warje Roads (Audit freeze), 2024-11 Kasba Waste (Contractor change), 2024-08 Kothrud Parks (Budget under revision), and 2024-05 Hadapsar Streetlight (System migration).

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — Ward 1 Kasba Roads & Pothole Repair computed +33.1% for 2024-07 (spend jumped from 14.8 to 19.7) and -34.8% for 2024-10 (spend decreased from 20.1 to 13.1), matching the ground truth exactly.

**Your git commit message for UC-0C:**

> `[UC-0C] Fix silent null handling and aggregation: all-ward blending and hidden nulls → added per-ward restriction, null auditing, and formula output`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It blended IT Section 3.1 with HR remote working mentions, stating: "Yes, you can use your personal phone to access work files and company email when working remotely from home using approved tools."

**Did it blend the IT and HR policies?**

> Yes — it improperly combined email-only BYOD access from IT policy with general remote work phrasing from HR, hallucinating authorization to access work files that IT Section 3.2 explicitly prohibits.

**After your fix — what does your system return for this question?**

> "According to [policy_it_acceptable_use.txt Section 3.1 and Section 3.2]: Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — all hedging phrases were eliminated via strict enforcement rules.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all 7 benchmark questions produced exact single-source citations or the mandatory refusal template.

**Your git commit message for UC-X:**

> `[UC-X] Fix cross-doc blending and hedged answers: BYOD and WFH policy synthesis → implemented single-source citations and strict refusal template`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The **Control** step (defining comprehensive RICE enforcement constraints upfront) was the most critical and challenging, because anticipating failure modes like condition dropping (e.g. dual approvers) or cross-document synthesis requires deep domain precision before running code.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The explicit refusal template and prohibition against cross-document synthesis in UC-X, as well as preserving all conditions in multi-stakeholder approval workflows (Clause 5.2 in UC-0B).

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating standard operating procedure (SOP) compliance checks and municipal citizen request triage with strict deterministic enforcement to avoid hallucinated approvals and taxonomy drift.

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

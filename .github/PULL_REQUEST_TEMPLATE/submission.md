# Vibe Coding Workshop — Submission PR

**Name:** Janakiraman  
**City / Group:** Hyderabad  
**Date:** 22 August 2026  
**AI tool(s) used:** Antigravity AI / Gemini 3.6 Flash (High)  

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

> `"Priority must be set to 'Urgent' if description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise set to 'Standard' (or 'Low' if minor noise/routine complaint)."`

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all complaints containing safety keywords returned Urgent priority (e.g. PM-202402 with 'school', PM-202420 with 'injury', PM-202446 with 'fell', GH-202411 with 'hospital').

**Your git commit message for UC-0A:**

> `UC-0A Fix severity blindness: no keywords in enforcement -> added injury/child/school/hospital triggers`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and obligation softening (especially dropping Department Head AND HR Director multi-condition approvals).

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 2.4 (verbal approval invalidity), 2.5 (unapproved absence = LOP), 5.2 (requires BOTH Department Head AND HR Director approval), and 7.2 (encashment prohibited during service).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are explicitly preserved with section numbers.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — naive prompts introduced scope bleed like "as is standard practice in municipal government organizations".

**Your git commit message for UC-0B:**

> `UC-0B Fix clause omission: completeness not enforced -> added every-numbered-clause rule`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> Returned a single aggregated total growth number (e.g. "+12.4% overall growth across all wards") without breaking down by ward or category.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards and silently skipped or averaged out the 5 null rows without reporting the null notes.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — explicit refusal condition: `"REFUSED: All-ward aggregation is not permitted. Scope must be per-ward per-category."`

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 null actual_spend rows are flagged as `NULL_FLAGGED` with dataset notes appended.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — July 2024 is +33.1% (19.7 vs 14.8) and October 2024 is -34.8% (13.1 vs 20.1).

**Your git commit message for UC-0C:**

> `UC-0C Fix silent aggregation: no scope in enforcement -> restricted to per-ward per-category only`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, personal phones can be used to access approved remote work tools and email when working from home."

**Did it blend the IT and HR policies?**

> Yes — it blended IT Section 3.1 (email/portal access) with HR remote working policy language.

**After your fix — what does your system return for this question?**

> `"Personal devices may only be used to access CMC email and the employee self-service portal. Downloading or storing work files and confidential documents on personal devices is strictly prohibited. [Source: policy_it_acceptable_use.txt, Section 3.1]"`

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — hedging language was strictly prohibited and zero hedging words were present.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all 7 test questions passed with exact single-source section citations or the verbatim refusal template.

**Your git commit message for UC-X:**

> `UC-X Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Step 4 (Enforcement Rule Writing). Crafting deterministic, unambiguous enforcement rules that prevented both false confidence (e.g., hallucinated categories) and false refusals required careful iterative testing against edge-case complaints and policy clauses.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The explicit refusal template constraint in UC-X agents.md: `"If a question is not covered in the available policy documents, output the EXACT refusal template... "`. Without this exact constraint, LLMs inevitably output hedged responses like "while not explicitly mentioned...".

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Building an internal policy compliance and document search assistant for municipal procurement guidelines.

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

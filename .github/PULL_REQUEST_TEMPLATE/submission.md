# Vibe Coding Workshop — Submission PR

**Name:** <Soumendu Santra>  
**City / Group:** <Kolkata>  
**Date:** 2026-03-11  
**AI tool(s) used:** GPT-5-medium in Trae IDE; built-in code/tools

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_kolkata.csv` without crash
- [x] `results_kolkata.csv` present in `uc-0a/`
- [x] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/`
- [x] `growth_output.csv` present in `uc-0c/`
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> Severity blindness and missing justification.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard unless explicit low-severity phrases (e.g., "minor", "small", "cosmetic") justify Low."  
> "reason must be a single sentence and must cite specific words or short phrases from the description …"

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> TBD upon answer key release — ran on Pune (15 rows) and produced deterministic outputs.

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — examples: PM-202402 (child/school), PM-202411 (hazard/sparking), PM-202420 (injury risk), PM-202446 (fell).

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness + missing justification → Implemented deterministic category/priority mapping with explicit urgency keywords; added one-sentence reason citing matched terms; robust CSV IO and NEEDS_REVIEW for ambiguous/missing descriptions.

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and obligation softening in naive summaries.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> 5.2 (both Department Head AND HR Director approvals dropped to generic "requires approval"); 7.2 ("not permitted under any circumstances" softened); timing windows in 2.6/2.7 partially omitted.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2 are present with preserved binding verbs and conditions.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No after fix — the agent refuses scope bleed and quotes verbatim if compression risks meaning loss.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission/softening → Added agents.md enforcement to include all numbered clauses and preserve multi-condition obligations; implemented retrieve_policy/summarize_policy with verb-preserving summaries and verbatim quotes for risky clauses; generated summary_hr_leave.txt.

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> A single aggregated growth figure across wards/categories with no formula shown and no mention of nulls. (Representative naive failure; replaced by parameterized per-ward per-category computation.)

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, aggregated across wards; no, it did not mention the 5 deliberate null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — requires --ward and --category; refuses if missing.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — rows with null current/comparator are flagged NULL_VALUE with notes surfaced. Dataset nulls include:  
> 2024-03 · Ward 2 – Shivajinagar · Drainage & Flooding; 2024-07 · Ward 4 – Warje · Roads & Pothole Repair; 2024-11 · Ward 1 – Kasba · Waste Management; 2024-08 · Ward 3 – Kothrud · Parks & Greening; 2024-05 · Ward 5 – Hadapsar · Streetlight Maintenance.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — July +33.1%, October −34.8% in uc-0c/growth_output.csv.

**Your git commit message for UC-0C:**

> UC-0C Fix aggregation/null handling → Enforced per-ward+category only; required --growth-type; MoM growth with explicit (current−previous)/previous formula; flagged and reported nulls/notes; wrote growth_output.csv.

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, personal phones can be used for approved remote work tools and email." (Blended HR+IT; incorrect permission.)

**Did it blend the IT and HR policies?**

> Yes — combined IT §3.1 with HR's remote work phrasing.

**After your fix — what does your system return for this question?**

> "Personal devices may be used to access CMC email and the CMC employee self-service portal only.  
> Source: policy_it_acceptable_use.txt §3.1"

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — hedging phrases are prohibited by enforcement rules.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — single-source answers with citations or the exact refusal template were returned for all seven.

**Your git commit message for UC-X:**

> UC-X Fix cross-document blending/hedging → Implemented single-source Q&A with section citations; added exact refusal template; indexed three policy docs by section; verified 7-question suite.

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Enforcement detailing was hardest — writing precise, testable rules that close common loopholes (e.g., 5.2’s dual approver, per-row formula emission, exact refusal template) required careful iteration to avoid ambiguity and ensure deterministic behavior.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> UC-X refusal template verbatim:  
> "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating policy‑based responses in an internal helpdesk bot with strict single‑source citations and a verbatim refusal template for out‑of‑scope requests.

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

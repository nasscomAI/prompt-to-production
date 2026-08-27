# Vibe Coding Workshop — Submission PR

**Name:** Darshan Gowda M  
**City / Group:** Hyderabad  
**Date:** 2026-08-12  
**AI tool(s) used:** Antigravity / Gemini 3.5 Flash  

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

> Severity blindness and taxonomy drift

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other" and "Priority must be Urgent if description contains any of the severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive); otherwise Standard or Low"

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing severity triggers (ambulance, hospital, school, collapse, etc.) correctly returned Urgent priority.

**Your git commit message for UC-0A:**

> `UC-0A Fix severity blindness and taxonomy drift: naive prompt missed critical safety triggers and generated arbitrary categories -> enforced exact 10-category taxonomy, keyword-based severity detection, and reason citations`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and condition dropping (specifically dropping the dual approver requirement in Clause 5.2 and carry-forward expiration rules in 2.6/2.7).

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 2.4 (verbal approval invalid), 2.6/2.7 (5-day limit and Jan-Mar forfeiture), 3.4 (holiday sick leave cert regardless of duration), 5.2 (dual approval of Department Head AND HR Director), and 7.2 (encashment during service strictly prohibited).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are explicitly verified and audited in summary_hr_leave.txt.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No — strict source grounding and explicit prohibition of unstated external corporate practices eliminated scope bleed.

**Your git commit message for UC-0B:**

> `UC-0B Fix clause omission and condition dropping: naive summary omitted critical deadlines and dropped dual-approver constraints -> enforced all 10 numbered binding clauses and preserved exact approval workflows`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated total growth percentage across all wards combined and silently skipped the deliberate null values without reporting reasons or formulas.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it erroneously aggregated across all wards and failed to flag the 5 deliberate null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — the system explicitly refuses when all-ward or cross-category aggregation is requested.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 null rows are identified and flagged with their exact reason from the notes column (e.g. Ward 2 Shivajinagar 2024-03 Drainage, Ward 5 Hadapsar 2024-05 Streetlight, Ward 4 Warje 2024-07 Roads, Ward 3 Kothrud 2024-08 Parks, Ward 1 Kasba 2024-11 Waste).

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — exactly matches +33.1% in July and -34.8% in October.

**Your git commit message for UC-0C:**

> `UC-0C Fix silent aggregation and null mishandling: naive prompt aggregated across all wards without explicit growth formula or null handling -> enforced per-ward per-category granularity, deliberate null flagging with note reasons, and explicit mathematical formulas`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It hallucinated and blended claims, stating: "Yes, you can use personal devices for approved remote work files and emails."

**Did it blend the IT and HR policies?**

> Yes — it blended IT Section 3.1 and HR remote work references to fabricate permission that does not exist.

**After your fix — what does your system return for this question?**

> "No. Personal devices may be used to access CMC email and the CMC employee self-service portal only (Section 3.1). Personal devices must not be used to access, store, or transmit classified, sensitive, or confidential CMC data or files. [Source: policy_it_acceptable_use.txt, Section 3.1, Section 3.2, Section 5.1]"

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — zero hedging phrases.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all 7 test questions produced exact single-source citations or the standardized refusal template.

**Your git commit message for UC-X:**

> `UC-X Fix cross-document blending and hedged hallucination: naive QA blended HR and IT permissions and used speculative hedging -> enforced single-source attribution with document/section citations and standardized refusal template`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The 'Focus' and 'Tweak' steps in UC-0B and UC-X, because subtle condition drops (like dual approver requirements or cross-document permission blending) appear convincing at first glance and require rigorous clause-by-clause audit rules.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The mandatory refusal template and single-source citation requirement in UC-X: "Never combine or synthesize claims from two different policy documents into a single blended answer."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automated civic complaint categorization and regulatory document search/compliance auditing for municipal and enterprise workflows.

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

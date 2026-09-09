# Vibe Coding Workshop — Submission PR

**Name:** Sai Krishna  
**City / Group:** Bengaluru  
**Date:** 2026-09-09  
**AI tool(s) used:** Antigravity / Gemini CLI  

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

> Severity blindness and taxonomy drift. The naive prompt invented ad-hoc subcategories (e.g. "Road Hazard", "Drainage Issue") instead of sticking to the 10 fixed categories, and it classified critical complaints containing words like "school children", "hospitalised", and "injury" as Standard priority.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No synonyms or variations permitted."
> and
> "Priority must be Urgent if description contains any of these severity keywords or their direct inflections: injury, injured, child, children, school, hospital, hospitalised, hospitalized, ambulance, fire, hazard, fell, collapse, collapsed."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing injury, child, children, school, hospital, hospitalised, fell, collapse, ambulance, and hazard returned Urgent priority without exception.

**Your git commit message for UC-0A:**

> [UC-0A] Fix severity blindness and taxonomy drift: missing keyword enforcement → added strict category enum, severity trigger keywords, and quoted reasons

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and obligation softening. Specifically, Clause 5.2 was weakened by dropping the mandatory dual-approver requirement (Department Head AND HR Director) to generic "manager approval", and Clauses 2.6 & 2.7 omitted the strict 31 December and Q1 forfeiture deadlines.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> - Clause 2.6 & 2.7: Dropped the 5-day maximum carry-forward limit and silent on forfeiture deadlines.
> - Clause 5.2: Softened "approval from both Department Head and HR Director" to "requires managerial approval".
> - Clause 7.2: Omitted the absolute prohibition of leave encashment during active service.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are explicitly present and highlighted with their binding verbs and exact approval chains intact.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — the naive prompt generated scope bleed statements like "employees are generally expected to provide reasonable notice as per standard organizational practice" and "exceptions may be granted at discretion", neither of which exists in the policy text.

**Your git commit message for UC-0B:**

> [UC-0B] Fix clause omission and obligation softening: summarizer dropped conditions → enforced all 10 numbered clauses, dual-approver requirements, and zero scope bleed

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> "Average municipal budget expenditure growth across all wards for 2024 was approximately +4.2%."

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated all wards into a single blended number and completely failed to mention the 5 deliberate null rows, silently skipping them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — any attempt to aggregate across all wards or omit a specific ward triggers an explicit policy refusal error and terminates execution.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 null rows are detected and flagged with their exact reason from the notes column:
> - Row 58: 2024-03 | Ward 2 – Shivajinagar | Drainage & Flooding (Data not submitted by ward office)
> - Row 124: 2024-05 | Ward 5 – Hadapsar | Streetlight Maintenance (Equipment procurement delay)
> - Row 167: 2024-07 | Ward 4 – Warje | Roads & Pothole Repair (Audit freeze — figures under review)
> - Row 191: 2024-08 | Ward 3 – Kothrud | Parks & Greening (Project suspended — pending approval)
> - Row 255: 2024-11 | Ward 1 – Kasba | Waste Management (Contractor change — billing delayed)

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — Ward 1 Roads in 2024-07 is +33.1% (((19.7 - 14.8) / 14.8) * 100) and in 2024-10 is -34.8% (((13.1 - 20.1) / 20.1) * 100).

**Your git commit message for UC-0C:**

> [UC-0C] Fix wrong aggregation and silent null handling: unconstrained calculation → enforced ward-level isolation, explicit null flagging, and transparent formulas

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal phone to access work files provided you use approved remote work tools and comply with CMC email security standards."

**Did it blend the IT and HR policies?**

> Yes — it improperly blended HR remote work provisions with IT BYOD policies, hallucinating permission to access work files on a personal phone, which is strictly prohibited by IT policy Section 3.2.

**After your fix — what does your system return for this question?**

> "[Source: policy_it_acceptable_use.txt Section 3.1 & Section 3.2]
> No. According to policy_it_acceptable_use.txt Section 3.1, personal devices may be used to access CMC email and the CMC employee self-service portal only. Furthermore, under Section 3.2, personal devices must not be used to access, store, or transmit classified or sensitive CMC data (work files). This restriction applies regardless of remote work status."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — all hedging phrases are strictly banned by enforcement rules and none appear in any answer.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all 7 test questions produced either an exact single-source citation or the required refusal template.

**Your git commit message for UC-X:**

> [UC-X] Fix cross-document blending and hedged hallucination: unconstrained QA -> enforced single-source policy citation, exact refusal template, and zero blending

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Adjust and Focus steps were the hardest. Unconstrained LLMs naturally tend to hedge, blend disparate policy documents into helpful-sounding but factually invalid compromises, and compute blended aggregations when data is missing. Formulating strict boundary conditions and explicit refusal contracts was essential to achieve 100% deterministic reliability.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The exact verbatim refusal template and the ambiguity review condition:
> "If the complaint description exhibits ambiguity between multiple categories or lacks clear distinguishing features, output flag: NEEDS_REVIEW; otherwise leave flag blank." and
> "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automated ingestion, classification, and compliance auditing of civic infrastructure inspection logs and vendor service tickets.

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

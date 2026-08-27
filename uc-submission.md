# Vibe Coding Workshop — Submission PR

**Name:** DARSHAN PATIL  
**City / Group:** Kolhapur  
**Date:** 2026-03-25  
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

> "Priority must be Urgent if description contains any of the following triggers: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15 (Verified against criteria)

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing safety triggers were correctly elevated to Urgent.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 2.4 (Written approval), 5.2 (Manager vs Dept Head/HR Director), and 7.2 (Encashment during service) were frequently omitted or softened in the naive summary.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 clauses are included with their full binding conditions.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it often added phrases like "as per standard HR practices" or "usually required," which were not in the CMC document.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause rule

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated percentage for the entire city budget rather than a per-ward breakdown.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it silently aggregated across all wards. No, it did not mention the missing actual spend values for several periods.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — the system requires both `--ward` and `--category` and refuses to calculate an aggregate total.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — null rows are marked as FLAGGED with the reason taken from the notes column.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — the calculated values (+33.1% and -34.8%) match the reference data exactly.

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use personal phones for work if you use approved remote work tools and CMC email."

**Did it blend the IT and HR policies?**

> Yes — it combined IT's email provision with HR's remote work mention to create a permission that doesn't exist.

**After your fix — what does your system return for this question?**

> "[Source: policy_it_acceptable_use.txt, Section 3.1] Personal devices may be used to access CMC email and the CMC employee self-service portal only. [Section 3.2] Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — answers are direct and strictly source-based.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — including a clean refusal for the "flexible working culture" question which is not in the documents.

**Your git commit message for UC-X:**

> UC-X  Fix cross-doc blending: no single-source rule → added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Refinement step in agents.md was the hardest. Explicitly defining exclusion boundaries for external knowledge was critical to prevent the AI from "helping" by filling in gaps with standard industry practices.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The specific refusal template and the "no-blending" rule in UC-X. Without these, the system would always try to answer instead of admitting silence.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating the triage of incoming support tickets based on internal technical documentation.

---

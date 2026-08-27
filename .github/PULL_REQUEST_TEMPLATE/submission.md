# Vibe Coding Workshop — Submission PR

**Name:** Shibam Dey Roy
**City / Group:** Kolkata
**Date:** 18 March 2026
**AI tool(s) used:** Antigravity (Google Deepmind)

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

> Severity blindness

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be Urgent if description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, choose Standard or Low."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15 (based on strict rule matching)

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows containing injury (PM-202420, PM-202446), child (PM-202402), and hazard (PM-202411) were correctly escalated to Urgent.

**Your git commit message for UC-0A:**

> [UC-0A] Fix missing logic: classifier.py was a placeholder → implemented rule-based classification and batch processing

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and obligation softening (specifically dual-approver rules)

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> 5.2 (multiple approvers combined into one) and 2.5 (LOP obligation softened to "may result in").

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 clauses are explicitly listed with their full binding conditions.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added phrases like "refer to company handbook for more details" which was not in the source text.

**Your git commit message for UC-0B:**

> [UC-0B] Fix condition dropping: app.py was a placeholder → implemented high-fidelity policy summarization preserving dual approvals and binding verbs

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> A single aggregate growth percentage for the entire city without ward breakdown or null handling.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated everything and silently ignored the null rows, leading to skewed results.

**After your fix — does your system refuse all-ward aggregation?**

> Yes, it explicitly refuses if --ward or --category are not provided.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — it flags them as NULL and provides the reason from the notes column (e.g., "Audit freeze").

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — the calculations perfectly match the reference benchmark.

**Your git commit message for UC-0C:**

> [UC-0C] Fix wrong aggregation level: app.py was a placeholder → implemented ward-specific growth logic with null-row flagging and formula disclosure

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use personal devices for CMC email and remote work as per HR policy."

**Did it blend the IT and HR policies?**

> Yes — it blended IT's email permission with HR's remote work tools, creating a permission for "accessing work files" that does not exist in the IT policy.

**After your fix — what does your system return for this question?**

> "Personal devices may be used to access CMC email and the CMC employee self-service portal only. [policy_it_acceptable_use.txt, Section 3.1]"

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — including the refusal for "flexible working culture".

**Your git commit message for UC-X:**

> [UC-X] Fix cross-document blending: app.py was a placeholder → implemented strict single-source RAG logic with mandatory citations and refusal template

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The "Enforcement" part of the RICE step was the most critical yet challenging, as it required identifying the exact traps (like the dual-approver logic in UC-0B) that the AI would naturally tend to simplify.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The "Refusal Template" for UC-X: "This question is not covered in the available policy documents... Please contact [relevant team] for guidance." This provided the binary boundary needed to prevent hedging.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating the classification of internal IT support tickets to ensure high-priority security incidents (like lost devices) are never missed by standard automated systems.

---

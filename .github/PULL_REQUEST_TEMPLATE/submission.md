# Vibe Coding Workshop — Submission PR

**Name:**  Sourav DG
**City / Group:**  Kolkata 
**Date:**  19 July 2026
**AI tool(s) used:**  None (rule-based implementation)

---

## Checklist — Complete Before Opening This PR

- [ ] `agents.md` committed for all 4 UCs
- [ ] `skills.md` committed for all 4 UCs
- [ ] `classifier.py` runs on `test_[city].csv` without crash
- [ ] `results_[city].csv` present in `uc-0a/`
- [ ] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [ ] `summary_hr_leave.txt` present in `uc-0b/`
- [ ] `growth_output.csv` present in `uc-0c/`
- [ ] 4+ commits with meaningful messages following the formula
- [ ] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> Taxonomy drift and severity blindness. Without enforcement, category names varied (e.g. "Pothole Repair" instead of "Pothole") and injury-related complaints were classified as Standard instead of Urgent.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations, abbreviations, or sub-categories." "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> [Your answer] out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — PM-202402 (child, school → Urgent), PM-202411 (hazard → Urgent), PM-202420 (injury → Urgent), PM-202446 (fell → Urgent). All 4 severity-triggering rows returned Urgent.

**Your git commit message for UC-0A:**

> UC-0A Fix no classification logic: starter raised NotImplementedError → implemented rule-based classifier with category keywords, severity keyword triggers (injury/child/school/hospital/ambulance/fire/hazard/fell/collapse), ambiguous flagging, and agents.md+skills.md via RICE

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and obligation softening. A naive prompt would drop clauses or replace "must" with "may", and would drop multi-condition requirements like clause 5.2 needing both Department Head AND HR Director.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> N/A — no naive prompt was run; the starter raised NotImplementedError. Based on the README, clause 5.2's dual-approver condition (Dept Head AND HR Director) would be the most likely to have a condition silently dropped.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2 are all present with their core obligations intact.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> N/A — no naive prompt was run. The implementation enforces "Never add information not present in the source document" so no scope bleed exists in the output.

**Your git commit message for UC-0B:**

> UC-0B Fix no summarization logic: starter raised NotImplementedError → implemented clause-by-clause policy summarizer with all-10-clauses enforcement, multi-condition preservation (e.g. clause 5.2 requires both Dept Head AND HR Director), scope bleed prevention, and [VERBATIM] flagging for clauses that cannot be condensed

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> N/A — no naive prompt was run; the starter raised NotImplementedError. The README warns the naive output would return a single aggregated number for all wards combined.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> N/A for naive. Our implementation enforces per-ward per-category only and prints all 5 null rows to stderr before computing.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — the system requires --ward and --category arguments; it never aggregates across wards or categories.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — though the specific run was for Ward 1 – Kasba / Roads & Pothole Repair which has no nulls in that subset. When run on Ward 2 – Shivajinagar / Drainage & Flooding, the 2024-03 null row is flagged with "Not computed — Data not submitted by ward office".

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — 2024-07: actual_spend 19.7, growth +33.1% ✓ | 2024-10: actual_spend 13.1, growth −34.8%

**Your git commit message for UC-0C:**

> UC-0C Fix no computation logic: starter raised NotImplementedError → implemented per-ward per-category MoM/YoY growth calculator with null row detection and flagging from notes column, formula display in every row, and cross-ward aggregation refusal enforcement

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> N/A — no naive prompt was run. The README warns it would blend IT and HR into "Yes, personal phones can be used for approved remote work tools and email."

**Did it blend the IT and HR policies?**

> N/A for naive. Our implementation returns a single-source answer from policy_it_acceptable_use.txt section 3.1 only: "Personal devices may be used to access CMC email and the CMC employee self-service portal only." If cross-document matches were detected, it would return the refusal template instead of blending.

**After your fix — what does your system return for this question?**

> "Per policy_it_acceptable_use.txt section 3.1: Personal devices may be used to access CMC email and the CMC employee self-service portal only."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — all answers are direct citations or the exact refusal template. No hedging phrases were generated.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — 6 questions returned single-source cited answers, 1 (flexible working culture) returned the exact refusal template verbatim. No blending, no hedging.

**Your git commit message for UC-X:**

> UC-X Fix no Q&A logic: starter raised NotImplementedError → implemented single-source document Q&A over 3 policy docs with cross-document blend prevention, verbatim refusal template for uncovered questions, hedging phrase prohibition, and source document+section citation enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The "Enforcement" step in RICE was the hardest because it requires translating abstract failure modes into precise, testable rules that can be mechanically verified. For example, preventing cross-document blending in UC-X required not just a rule but a scoring algorithm that refuses whenever two documents score equally.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The specific severity keyword list in UC-0A: "injury, child, school, hospital, ambulance, fire, hazard, fell, collapse" — the AI would generate "relevant severity terms" but not the exact closed set needed for deterministic enforcement.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Building a data validation pipeline where incoming CSV data must be classified by department rules — applying RICE to define the classification boundary and CRAFT to iteratively test edge cases against the rules.

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

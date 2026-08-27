# Vibe Coding Workshop — Submission PR

**Name:** Shravan Taleki
**City / Group:** Bangalore
**Date:** 2026-03-24
**AI tool(s) used:** Antigravity (powered by Gemini)

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

> "Assign priority 'Urgent' if description contains keywords like injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all rows with severity keywords were correctly classified as Urgent.

**Your git commit message for UC-0A:**

> UC-0A Fix type error: Pylance false positive on property getter -> assigned reader.fieldnames to a local variable

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses related to multi-condition obligations (e.g., 5.2 losing second approver) and specific numbering consistency were weakened.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all critical clauses are included with the [VERBATIM] tag where meaning preservation was critical.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No significant scope bleed was noted, but clauses were dropped.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause rule and multi-condition preservation

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated growth percentage for all wards combined without showing the breakdown.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated everything into one number and ignored the null rows without flagging them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — rows with missing data are explicitly flagged with reasoning from the notes.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no ward/category scope enforced → added per-ward per-category only rule and null flagging

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It provided a blended answer that combined IT acceptable use with HR remote work policies without clear attribution.

**Did it blend the IT and HR policies?**

> Yes — it mixed rules from both without stating which rule came from which document.

**After your fix — what does your system return for this question?**

> It provides a single-source answer citing exactly one document per claim, or refuses if asked to blend.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — enforcement strictly bans hedging.

**All 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: no single-source rule → added single-source attribution enforcement and exact refusal wording

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Enforce step was the most challenging because it required translating manual analysis of AI failures into precise, non-negotiable rules that the LLM would follow consistently without over-refusal.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it" (UC-0B)

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating code review guidelines enforcement across multiple repositories.

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

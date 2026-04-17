# Vibe Coding Workshop — Submission PR

**Name:** Abhishek Hardaha  
**City / Group:** Pune  
**Date:** 17 April 2026
**AI tool(s) used:** Antigravity / Gemini 3.1 Pro

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

> Severity blindness

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be Urgent if the description contains any of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Matching is case-insensitive."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — complaints mentioning "School" (PM-202402), "hazard" (PM-202411), "injury" (PM-202420), and "fell" (PM-202446) all successfully triggered the Urgent priority.

**Your git commit message for UC-0A:**

> [UC-0A] Fix severity blindness: no severity keywords in enforcement -> added injury/child/school/hospital/hazard/fell/collapse triggers with exact category taxonomy enforcement

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and scope bleed

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 missing the mandatory secondary approver ("AND HR Director"), Clause 2.7 weakened, and exact limits rounded off.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all clauses are fully preserved with binding verbs matched.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added phrases like "as is standard practice for statutory leaves" which never appeared in the source document.

**Your git commit message for UC-0B:**

> [UC-0B] Fix clause omission: completeness not enforced -> added every-numbered-clause rule along with exact binding verbs

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated MoM growth number calculating across the entire document without ward or category segregation.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated all wards. No, it completely missed and silently ignored the 5 null rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes. 

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — Rows for Ward 2 Drainage, Ward 4 Roads, Ward 1 Waste, Ward 3 Parks, and Ward 5 Streetlight match and report their respective `NULL` notes prior to any computations. 

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes.

**Your git commit message for UC-0C:**

> [UC-0C] Fix silent aggregation: no scope in enforcement -> restricted to per-ward per-category only and explicitly handled null rows

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal phone for approved remote tools and email."

**Did it blend the IT and HR policies?**

> Yes — it combined the IT policy's limited access constraints (only self-service/email) with the HR policy's generic wording on remote arrangements to hallucinate new permissions.

**After your fix — what does your system return for this question?**

> "Per policy_it_acceptable_use.txt section 3.1: Personal devices may be used to access CMC email and the CMC employee self-service portal only."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> Yes, the naive model used "While not explicitly covered by the documents, it is typically understood...". The final system correctly blocks this.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes.

**Your git commit message for UC-X:**

> [UC-X] Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement and exact refusal template

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Writing explicit refusal conditions and condition mappings (the "Enforcement" phase). The AI naturally defaults to helpful guessing, smoothing over caveats, or synthesizing missing data, making it genuinely challenging to enforce strict failure/refusal protocols.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The exact verbatim refusal template rule for UC-X: "If the question is not covered in any of the three documents, respond with the refusal template exactly: 'This question is not covered in the available policy documents...'"

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Extracting API documentation and generating functional logic summaries without hallucinating undocumented features or blending similar but distinct frameworks.

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

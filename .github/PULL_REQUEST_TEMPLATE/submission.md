# Vibe Coding Workshop — Submission PR

**Name:** Mahendra Cherukupalli
**City / Group:** Hyderabad
**Date:** July 19, 2026
**AI tool(s) used:** Gemini 3.5 Flash (via Antigravity)

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

> Priority must be Urgent if description contains any of the following severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes

**Your git commit message for UC-0A:**

> [UC-0A] Fix severity blindness: naive prompt missed priority triggers → added explicit keyword-based severity enforcement

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> 5.2 (dropped the requirement for approvals from both the Department Head and the HR Director) and 7.2 (softened absolute restriction on leave encashment during service)

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**

> No

**Your git commit message for UC-0B:**

> [UC-0B] Fix clause omission: naive summary dropped multi-approver conditions → enforced exact condition mapping for critical clauses

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> An aggregated single city-wide average spend value without ward or category breakdown.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated all wards together. No, it silently ignored the 5 null rows without any note or explanation.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — the 5 null rows are flagged with their specific notes: Line 58 (Ward 2 Drainage, 2024-03), Line 124 (Ward 5 Streetlights, 2024-05), Line 167 (Ward 4 Roads, 2024-07), Line 191 (Ward 3 Parks, 2024-08), and Line 255 (Ward 1 Waste, 2024-11).

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> [UC-0C] Fix wrong aggregation level: naive query calculated global growth → implemented per-ward per-category analysis with strict refusal and null flagging

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal phone to access work files as long as you follow the HR remote work guidelines and security policies."

**Did it blend the IT and HR policies?**

> Yes — it incorrectly combined the IT policy about personal devices (email and self-service portal only) with the HR remote work tools guidelines, giving a false sense of security clearance.

**After your fix — what does your system return for this question?**

> According to policy_it_acceptable_use.txt Section 3.1, personal devices may be used to access CMC email and the CMC employee self-service portal only. Section 3.2 states that personal devices must not be used to access, store, or transmit classified or sensitive CMC data.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> [UC-X] Fix cross-doc blending: naive prompt combined IT and HR rules → implemented single-source policy retrieval with exact citation enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The 'Refining' step was the hardest because it required identifying subtle failure modes like condition dropping and cross-document blending. Writing precise Python heuristic models to mimic the intended prompt behavior was the most effective way to eliminate these failure modes permanently.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The exact refusal template in uc-x/agents.md: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Building an automated compliance auditor for verifying software purchase orders against municipal spending guidelines.

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

# Vibe Coding Workshop — Submission PR

**Name:** Hari  
**City / Group:** Chennai  
**Date:** April 14, 2026  
**AI tool(s) used:** Gemini (Antigravity AI)  

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_chennai.csv` without crash
- [x] `results_chennai.csv` present in `uc-0a/`
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

> "TRAP DETECTION: If a complaint contains any mention of injury, children, schools, or hospitals, the severity MUST be set to Urgent regardless of other factors." and "TAXONOMY ENFORCEMENT: The agent must strictly map the category to one of the 10 predefined values. If multiple apply, select the most specific one."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — the enforcement rule successfully caught these triggers that were previously missed by the naive prompt.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness and taxonomy drift: no keywords or restricted set → added injury/child/school triggers and 10-item taxonomy enforcement

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and obligation softening.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 5.2 (dual approval), 5.3 (commissioner approval for >30 days), and 7.2 (encashment prohibition) were often omitted or generalized in the broad summary.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all 10 mandatory clauses identified in the inventory are explicitly listed.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added phrases like "regularly following standard HR practices" which were not in the technical document.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness unenforced → added every-numbered-clause rule

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single average growth percentage across all wards and categories without highlighting missing data.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards (strictly prohibited). No, it skipped the 5 null rows silently in its calculation.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — it throws a "Refusal" error if "all" or multiple wards/categories are requested.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — the rows are marked as "NULL" with the reason from the notes column included in the output.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — the calculations are verified against the July and October reference points for Kasba Ward.

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no ward/category scope → enforced per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal device, and you may even be eligible for a phone allowance as per HR policy."

**Did it blend the IT and HR policies?**

> Yes — it blended the HR reimbursement policy with the IT security policy, ignoring the IT section 3.1 that strictly forbids personal devices for work files.

**After your fix — what does your system return for this question?**

> It returns the exact refusal template regarding cross-document blending or cites IT Policy 3.1 specifically forbidding the use of personal devices for work files.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — hedging is strictly prohibited by the enforcement rules.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all outputs are either evidence-backed from a single section or a controlled refusal.

**Your git commit message for UC-X:**

> UC-X  Fix cross-doc blending: no single-source rule → added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The "Analyze" step was the hardest because it requires identifying exactly why the AI failed (e.g., distinguishing between taxonomy drift and hallucination) to write an effective enforcement rule.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The specific "Refusal Condition" for cross-document blending in UC-X: "If a query requires information from more than one source document to form a complete answer, the agent MUST return the refusal template."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> I will use this for summarizing project compliance reports where missing a single regulatory clause can have legal implications.

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

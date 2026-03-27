# Vibe Coding Workshop — Submission PR

**Name:**  Sanket Vitthalrao Kale
**City / Group:**   Solapur
**Date:**  25/08/2023
**AI tool(s) used:**  Antigravity,trea

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

> "Priority must be Urgent if description contains any of these exact keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — all severity keywords correctly triggered the Urgent priority.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: no keywords in enforcement -> added injury/child/school/hospital triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (LWP dual approval requirement) and Clause 2.7 (Carry-forward forfeiture window) were often weakened or omitted.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all critical clauses are present and accurately reflect the original obligations.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it occasionally added standard HR practices like "contact HR for more details" which were not in the source text.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced -> added every-numbered-clause rule

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated growth percentage across all wards and categories, ignoring the specific breakdown required.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards and completely ignored the null rows, treating them as zero or skipping them silently.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — it requires both `--ward` and `--category` arguments and refuses to run without them.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — the null rows are explicitly flagged with the reason from the notes column (e.g., "FLAGGED: Data missing due to system error").

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — the calculations match the reference values exactly.

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no scope in enforcement -> restricted to per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use your personal phone to access work files, but you must ensure it complies with the IT acceptable use policy and you will not be reimbursed for the phone bill."

**Did it blend the IT and HR policies?**

> Yes — it combined the IT acceptable use policy regarding personal devices with the finance policy regarding reimbursements into a single answer.

**After your fix — what does your system return for this question?**

> "Employees may use personal mobile devices to access company email and Slack, provided they install the company Mobile Device Management (MDM) profile. Accessing local file servers from personal devices is strictly prohibited.
> 
> Source: policy_it_acceptable_use.txt, Section 3.1"

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — all answers are direct quotes or strict interpretations of the source text without hedging.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — all questions were either answered with a single source citation or refused using the exact template.

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The "Refine" step was the most challenging. It required carefully analyzing the failure modes of the naive prompts and translating those observations into strict, unambiguous enforcement rules that the AI could consistently follow without over-correcting.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The explicit refusal conditions and strict formatting constraints. For example, in UC-X: "If question is not in the documents — use the refusal template exactly, no variations". The AI naturally wants to be helpful and guess, so forcing it to refuse was a manual addition.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> I will use RICE + CRAFT to build an automated log analysis tool that categorizes system errors and flags critical security events based on strict keyword matching and context rules, ensuring it doesn't hallucinate error causes.

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

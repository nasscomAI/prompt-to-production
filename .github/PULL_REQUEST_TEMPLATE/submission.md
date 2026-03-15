# Vibe Coding Workshop — Submission PR

**Name:Chadalla Naveen**  
**City / Group:**Nellore /   
**Date:**  
**AI tool(s) used:**  

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

> severity blindness

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

>"The priority must be set to 'Urgent' if any of the following severity keywords are present in the description: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes 

**Your git commit message for UC-0A:**

> UC-0A Fix multiple failure modes: implemented RICE framework in agents.md, skills.md, and classifier.py with strict taxonomy, severity keywords, and ambiguity flagging

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> All three

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (Weakened): The naive output stated "LWP requires approval," dropping the critical requirement for approval from both the Department Head and HR Director.
Clause 2.7 (Missing): The requirement to use carry-forward days within the first quarter (Jan–Mar) was omitted in the summary.
Clause 7.2 (Missing/Omitted): The absolute prohibition of leave encashment during service was often left out of the high-level summary.
Clause 3.4 (Weakened): The condition that certs are required for leave before/after holidays regardless of duration was simplified to a general "medical certs required" statement

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes 

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes. The naive summary included phrases like "as is standard practice in HR" and "typically, employees are expected to notify managers," none of which were in the source text. It also hallucinated that bereavement leave followed "company-standard policies" (which don't exist in the provided text).

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission · obligation softening · scope bleed: naive prompt drops dual-approver conditions (5.2) and injects external HR context → implemented RICE agent with rule-based verbatim extraction for multi-condition clauses and zero-external-knowledge enforcement.

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> The naive prompt returned a single aggregated growth percentage for the entire dataset across all wards and categories, choosing MoM growth silently.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated all wards into a single result. No, it did not mention the 5 null rows; it likely treated them as 0 or skipped them entirely without alerting the user.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — the following rows are explicitly flagged in the output with their reason from the notes column:

2024-03 · Ward 2 – Shivajinagar · Drainage & Flooding
2024-07 · Ward 4 – Warje · Roads & Pothole Repair
2024-11 · Ward 1 – Kasba · Waste Management
2024-08 · Ward 3 – Kothrud · Parks & Greening
2024-05 · Ward 5 – Hadapsar · Streetlight Maintenance

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes 

**Your git commit message for UC-0C:**

> UC-0C Fix all three failure modes: silent aggregation + null skipping + formula assumption → implemented load_dataset with null flagging, compute_growth with per-row formula output including flagged nulls, and CLI refusal when --growth-type is unspecified.

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use personal devices for work. According to the IT policy, you can use personal phones to access CMC email and the employee self-service portal. The HR policy also mentions approved remote work tools, and the Finance policy provides an Rs 8,000 allowance for home office equipment like networking tools which can help with remote access."

**Did it blend the IT and HR policies?**

> Yes 

**After your fix — what does your system return for this question?**

> PERSONAL DEVICES (BYOD) 3.1 Personal devices may be used to access CMC email and the CMC employee self-service portal only. Source: policy_it_acceptable_use.txt, section 3

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

>No — The system is strictly grounded in the provided text. If a match is found, it returns the raw section text and citation. If no match is found, it uses the mandatory refusal template verbatim.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes 

**Your git commit message for UC-X:**

> UC-X Fix [cross-document blending]: Naive retrieval synthesized HR and IT policies into incorrect permissions → Implemented RICE enforcement with IDF-weighted single-source scoring and a document-blending guard.

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The hardest CRAFT step across the use cases was Refinement. It required carefully reviewing the AI-generated output and identifying gaps, inconsistencies, or missing rules that the AI could not infer from context.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> i didn't add anything manually. i just reviewed the output.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> If i wanted to build any project i can use this RICE + CRAFT method to build each feature in the project.

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

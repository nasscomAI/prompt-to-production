Vibe Coding Workshop — Submission PR

Name: Vaishnavi Chinthakunta
City / Group: Nellore
Date: 16 March 2026
AI tool(s) used: ChatGPT

---

Checklist — Complete Before Opening This PR

- [x] "agents.md" committed for all 4 UCs
- [x] "skills.md" committed for all 4 UCs
- [x] "classifier.py" runs on "test_[city].csv" without crash
- [x] "results_[city].csv" present in "uc-0a/"
- [x] "app.py" for UC-0B, UC-0C, UC-X — all run without crash
- [x] "summary_hr_leave.txt" present in "uc-0b/"
- [x] "growth_output.csv" present in "uc-0c/"
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

---

UC-0A — Complaint Classifier

Which failure mode did you encounter first?
(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)

«Severity blindness»

What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:

«If the complaint contains safety signals such as injury, hospital, school, or child, the classifier must assign severity = Urgent regardless of category.»

How many rows in your results CSV match the answer key?

«13 out of 15»

Did all severity signal rows (injury/child/school/hospital) return Urgent?

«Yes»

Your git commit message for UC-0A:

«feat(uc-0a): implement complaint classifier with severity rule»

---

UC-0B — Summary That Changes Meaning

Which failure mode did you encounter?
(clause omission / scope bleed / obligation softening)

«Clause omission»

List any clauses that were missing or weakened in the naive output (before your RICE fix):

«Leave approval requirement and manager notification clause were missing.»

After your fix — are all 10 critical clauses present in summary_hr_leave.txt?

«Yes»

Did the naive prompt add any information not in the source document (scope bleed)?

«No»

Your git commit message for UC-0B:

«feat(uc-0b): generate HR leave policy summary with clause preservation»

---

UC-0C — Number That Looks Right

What did the naive prompt return when you ran "Calculate growth from the data."?

«The naive output returned an overall growth percentage without ward separation.»

Did it aggregate across all wards? Did it mention the 5 null rows?

«Yes, it aggregated across all wards and ignored the null rows.»

After your fix — does your system refuse all-ward aggregation?

«Yes»

Does your growth_output.csv flag the 5 null rows rather than skipping them?

«Yes — null rows are flagged instead of skipped.»

Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?

«Yes»

Your git commit message for UC-0C:

«feat(uc-0c): implement ward-wise growth calculation and null row detection»

---

UC-X — Ask My Documents

What did the naive prompt return for the cross-document test question?
(Question: "Can I use my personal phone to access work files when working from home?")

«The naive output mixed HR and IT policies and gave a general answer without citing the correct document.»

Did it blend the IT and HR policies?

«Yes»

After your fix — what does your system return for this question?

«Access to work files from personal devices is governed by the IT Acceptable Use Policy. Personal phones may only be used if they meet the organization's security requirements.»

Did your system use any hedging phrases in any answer?
("while not explicitly covered", "typically", "generally understood")

«No»

Did all 7 test questions produce either a single-source cited answer or the exact refusal template?

«Yes»

Your git commit message for UC-X:

«feat(uc-x): implement cross-document policy Q&A system»

---

CRAFT Loop Reflection

Which CRAFT step was hardest across all UCs, and why?

«The hardest step was the “Refine” stage because I had to adjust prompts and rules multiple times to avoid incorrect outputs and ensure the system followed strict rules.»

What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?

«The enforcement rule requiring urgent classification when safety-related keywords appear in complaints.»

Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:

«Automating complaint classification for city service requests using structured prompts and validation rules.»

---

Reviewer Notes (tutor fills this section)

Criterion| Score /4| Notes
RICE prompt quality| | 
agents.md quality| | 
skills.md quality| | 
CRAFT loop evidence| | 
Test coverage| | 
Total| /20| 

Badge decision:

- [ ] Standard badge — meets pass threshold (score 11+/20 on this review, full rubric 22+/40)
- [ ] Distinction badge — meets distinction threshold (score 17+/20 on this review, full rubric 34+/40)
- [ ] Not yet — resubmit after addressing: _______________
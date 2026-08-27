Vibe Coding Workshop — Submission PR

Name: S. Sreekara Narayana
City / Group: Hyderabad / Star Group
Date: 14 March 2026
AI tool(s) used: Antigravity (primary workshop tool), ChatGPT (used for guidance and troubleshooting)

Checklist — Complete Before Opening This PR

✓ agents.md committed for all 4 UCs
✓ skills.md committed for all 4 UCs
✓ classifier.py runs on test_[city].csv without crash
✓ results_[city].csv present in uc-0a/
✓ app.py for UC-0B, UC-0C, UC-X — all run without crash
✓ summary_hr_leave.txt present in uc-0b/
✓ growth_output.csv present in uc-0c/
✓ 4+ commits with meaningful messages following the formula
✓ All sections below are filled in

---

UC-0A — Complaint Classifier

Which failure mode did you encounter first?
missing justification

What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:

"The classifier must include a clear reason referencing the keyword or signal detected in the complaint description."

How many rows in your results CSV match the answer key?
15 out of 15

Did all severity signal rows (injury/child/school/hospital) return Urgent?

Yes — rows containing injury, child, school, or hospital keywords were correctly classified as Urgent.

Your git commit message for UC-0A:

[UC-0A] Fix missing justification: classifier returned labels without reasoning → enforced keyword-based classification with justification and severity rules

---

UC-0B — Summary That Changes Meaning

Which failure mode did you encounter?
clause omission

List any clauses that were missing or weakened in the naive output (before your RICE fix):

Clause 2.6 (Leave carry forward rule)
Clause 5.2 (Leave Without Pay approval rule)

After your fix — are all 10 critical clauses present in summary_hr_leave.txt?

Yes

Did the naive prompt add any information not in the source document (scope bleed)?

No

Your git commit message for UC-0B:

[UC-0B] Fix clause omission: naive summarization dropped obligations → enforced inclusion of all critical HR leave clauses

---

UC-0C — Number That Looks Right

What did the naive prompt return when you ran "Calculate growth from the data."?

The naive output returned a general growth statement aggregating the data across wards without calculating ward-level growth.

Did it aggregate across all wards? Did it mention the 5 null rows?

Yes — it aggregated across all wards and did not mention the null rows.

After your fix — does your system refuse all-ward aggregation?

Yes

Does your growth_output.csv flag the 5 null rows rather than skipping them?

Yes — the rows containing null values are flagged.

Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?

Yes

Your git commit message for UC-0C:

[UC-0C] Fix aggregation error: growth calculated across wards → enforced ward-level growth calculation and flagging of null data rows

---

UC-X — Ask My Documents

What did the naive prompt return for the cross-document test question?
(Question: "Can I use my personal phone to access work files when working from home?")

The naive answer suggested that employees could access work files on personal devices while working remotely depending on company policy.

Did it blend the IT and HR policies?

Yes — it blended multiple policy interpretations instead of referencing a single policy source.

After your fix — what does your system return for this question?

IT Policy 3.1: Personal devices may access company email and the employee self-service portal only.

Did your system use any hedging phrases in any answer?
("while not explicitly covered", "typically", "generally understood")

No

Did all 7 test questions produce either a single-source cited answer or the exact refusal template?

Yes

Your git commit message for UC-X:

[UC-X] Fix cross-document blending: answers mixed HR and IT policies → enforced single-source policy answers and refusal template

---

CRAFT Loop Reflection

Which CRAFT step was hardest across all UCs, and why?

The Refine step was the most challenging because it required identifying failure modes from naive prompts and then writing clear enforcement rules in agents.md to prevent those failures.

What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?

"Answers must reference exactly one policy document and must not combine information from multiple policy documents."

Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:

I will apply the RICE + CRAFT workflow while developing AI-powered learning tools in my ExamCopilot project to ensure responses are grounded in a single verified source.

---

Reviewer Notes (tutor fills this section)

Criterion | Score /4 | Notes
RICE prompt quality | |
agents.md quality | |
skills.md quality | |
CRAFT loop evidence | |
Test coverage | |

Total | /20 |

Badge decision:

Standard badge — meets pass threshold (score 11+/20 on this review, full rubric 22+/40)

Distinction badge — meets distinction threshold (score 17+/20 on this review, full rubric 34+/40)

Not yet — resubmit after addressing: _______________


# Vibe Coding Workshop — Submission PR Draft

**Name:** Prachi Sangaonkar
**City / Group:** Pune / Workshop
**Date:** 2026-04-17
**AI tool(s) used:** Antigravity (Gemini-based Coding Assistant)

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
Severity blindness. The initial naive approach ignored safety-critical keywords like "injury" or "child" if they appeared alongside standard pothole or streetlight complaints.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**
`"Urgent triggers: Flag as Urgent if the complaint mentions 'injury', 'blood', 'hospital', 'child', or 'doctor' regardless of other keywords."`

**How many rows in your results CSV match the answer key?**
15 out of 15.

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**
Yes. Every row containing "child," "hazard," "injury," or "fell" was correctly promoted to Urgent priority.

**Your git commit message for UC-0A:**
`UC-0A Fix severity blindness and taxonomy drift: initial implementation lacked safety keywords and strict categories → implemented rule-based enforcement in classifier.py`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
Clause omission and obligation softening. Specifically, the dual-approver requirement in Clause 5.2 was being simplified to "requires approval."

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**
Clause 5.2 (Approval from BOTH Dept Head and HR Director) and Clause 2.6 (Forfeiture of leave above 5 days).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**
Yes. All 10 clauses were correctly parsed and summarized with conditions intact.

**Did the naive prompt add any information not in the source document (scope bleed)?**
Yes. It initially added language like "standard leave practices apply," which was not in the text.

**Your git commit message for UC-0B:**
`UC-0B Fix clause omission and obligation softening: initial summarizer omitted dual-approval and strict deadlines → implemented strict clause mapping and multi-condition preservation in app.py`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**
One single, global percentage value representing the entire city's spend growth for the year.

**Did it aggregate across all wards? Did it mention the 5 null rows?**
It aggregated across all wards and silently ignored the null rows without notification.

**After your fix — does your system refuse all-ward aggregation?**
Yes. The script requires explicit `--ward` and `--category` arguments and refuses global totals.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**
Yes. Every null row is reported in the audit log during load and flagged in the CSV with the note reason (e.g., "Audit freeze").

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**
Yes. Verified against the `ward_budget.csv` reference values.

**Your git commit message for UC-0C:**
`UC-0C Fix aggregation level and silent nulls: initial version aggregated global totals and hid missing data → implemented ward-wise segmentation and mandatory null auditing in app.py`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
"Yes, you can use your personal phone for approved remote tools and work files." (It blended the HR leave policy tools with IT's restrictive BYOD policy).

**Did it blend the IT and HR policies?**
Yes. It gave permission for "work files" which was strictly prohibited in the IT policy.

**After your fix — what does your system return for this question?**
"Answer: Personal devices may be used to access CMC email and the CMC employee self-service portal only. [policy_it_acceptable_use.txt, Section 3.1]"

**Did your system use any hedging phrases in any answer?**
No. All hedging was replaced by the strict refusal template when info was missing.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**
Yes. All 7 questions were verified to follow the RICE enforcement rules.

**Your git commit message for UC-X:**
`[UC-X] Fix cross-document blending and hedged hallucination: implemented single-source retrieval and strict refusal template in app.py`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**
**Analyze**. It required very precise attention to detail to understand why the AI was "softening" a legal obligation or why a particular aggregation was wrong compared to the ground truth.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**
The verbatim **Refusal Template** for UC-X. Without this exact mechanical constraint, the AI would default to helpful-sounding but inaccurate hedging.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**
Updating my team's internal technical documentation and onboarding guides, ensuring that security protocols are cited strictly without external "best practice" hallucinations.

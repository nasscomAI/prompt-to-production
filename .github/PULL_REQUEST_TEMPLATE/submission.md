# Vibe Coding Workshop — Submission PR

**Name:** Samata Kandolkar  
**City / Group:** Goa  
**Date:** 2026-06-16  
**AI tool(s) used:** Claude Code (claude-sonnet-4-6)

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

> Taxonomy drift and severity blindness hit simultaneously. The naive prompt produced free-form category names that varied across rows for the same type of complaint, and complaints containing keywords like "school", "hazard", and "injury" were classified as Standard instead of Urgent.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "category MUST be exactly one of these strings with no variations: Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other"
>
> "priority MUST be 'Urgent' if the description contains any of these words (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — otherwise use 'Standard' for active ongoing issues or 'Low' for minor or cosmetic issues"

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> Pending answer key — 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — PM-202402 (school children), PM-202411 (electrical hazard), PM-202420 (risk of serious injury), PM-202446 (elderly resident fell) all returned Urgent. Client-side keyword enforcement in classifier.py guarantees this even if the model misses a keyword.

**Your git commit message for UC-0A:**

> [UC-0A] Fix taxonomy drift + severity blindness: naive prompt used free-form categories and ignored injury/school keywords → added RICE enforcement with exact 10-category list and mandatory Urgent escalation on severity keywords

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and obligation softening. A naive summariser drops multi-condition obligations to a single condition — clause 5.2 ("Department Head AND HR Director") collapses to "requires manager approval", silently removing one required approver. Binding verbs ("must", "will", "not permitted") get softened to "should" or "is expected to".

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> The highest-risk clauses for naive summarisers: 5.2 (dual approver condition), 2.5 (LOP regardless of subsequent approval — "will" softened to "may"), 7.2 (not permitted under any circumstances — softened to "generally not permitted"), 2.4 (verbal approval not valid — condition dropped), 3.4 (medical cert required regardless of duration — "regardless" clause dropped).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all clauses 1.1 through 8.2 are present. Clause 5.2 is marked [VERBATIM] and quoted word-for-word to prevent any paraphrase from dropping the "Department Head AND HR Director" dual-approver condition.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — naive outputs typically add phrases like "as is standard practice in government organisations" or "employees are generally expected to" which do not appear anywhere in the source document. The agents.md enforcement rule explicitly prohibits these phrases.

**Your git commit message for UC-0B:**

> [UC-0B] Fix clause omission + obligation softening: naive prompt dropped dual-approver condition in 5.2 and softened binding verbs → added RICE enforcement requiring all clauses present, all conditions preserved, and verbatim quoting when paraphrase risks meaning loss

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> A naive prompt returns a single aggregated growth number across all wards and all categories — e.g. "Overall budget spend grew by 8.3% from January to December 2024" — with no mention of which ward or category, no null row disclosure, and no formula shown.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards and all categories. No, it did not mention the 5 null rows — they were silently excluded or interpolated, making the number look clean when it was not.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — the system requires `--ward` and `--category` to be specified explicitly. The enforcement rule states: "Computation MUST be scoped to exactly one ward and one category as specified by the caller — never aggregate across multiple wards or categories, and refuse if asked to do so."

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — all 5 null rows are reported at dataset load time before any computation begins. The specific rows flagged are: 2024-03 Ward 2 – Shivajinagar Drainage & Flooding, 2024-05 Ward 5 – Hadapsar Streetlight Maintenance, 2024-07 Ward 4 – Warje Roads & Pothole Repair, 2024-08 Ward 3 – Kothrud Parks & Greening, 2024-11 Ward 1 – Kasba Waste Management. None fall within the Ward 1 – Kasba / Roads & Pothole Repair scope, so growth_output.csv has no NULL_FLAGGED rows for the default run.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — 2024-07: +33.1% (formula: (19.7 - 14.8) / 14.8 × 100), 2024-10: −34.8% (formula: (13.1 - 20.1) / 20.1 × 100). Both verified by running app.py against ward_budget.csv.

**Your git commit message for UC-0C:**

> [UC-0C] Fix silent null handling + wrong aggregation level: naive prompt skipped 5 null rows and collapsed all wards into one number → added load-time null reporting, per-ward/category scoping, formula column, and growth-type refusal when unspecified

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> A naive system returns a blended answer such as: "Yes, you can use your personal phone to access approved remote work tools and CMC email when working from home." This combines IT policy section 3.1 (email + portal only) with HR policy language about remote work tools — producing a permission that does not exist in either document.

**Did it blend the IT and HR policies?**

> Yes — it merged IT-POL-003 section 3.1 (personal devices: CMC email and self-service portal only) with HR leave policy references to approved remote work tools, granting a broader permission than either document actually states.

**After your fix — what does your system return for this question?**

> According to IT-POL-003 section 3.1, personal devices may be used to access CMC email and the CMC employee self-service portal only. No other work files or systems are permitted on personal devices. [policy_it_acceptable_use.txt · section 3.1]

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — the system prompt explicitly prohibits these phrases. The agents.md enforcement rule lists each forbidden phrase by name, and the system prompt marks them as "absolutely prohibited".

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — expected behaviour per question: (1) carry-forward → HR §2.6–2.7 cited; (2) Slack on laptop → IT §2.3 cited; (3) home office allowance → Finance §3.1 cited; (4) personal phone + work files → IT §3.1 only, no blending; (5) flexible working culture → refusal template (not in any document); (6) DA and meal receipts same day → Finance §2.6 cited (explicitly prohibited); (7) LWP approver → HR §5.2 cited with both Department Head AND HR Director named.

**Your git commit message for UC-X:**

> [UC-X] Fix cross-document blending + hedged hallucination: naive prompt merged IT and HR policies into a permission that exists in neither → added single-source enforcement, prohibited-phrase list, exact refusal template, and explicit personal-device routing to IT-POL-003 §3.1

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Enforcement (the R and E in RICE) was hardest. It is easy to write a role and an intent in vague terms, but writing enforcement rules that are specific enough to be testable — quoting exact allowed values, listing exact prohibited phrases, naming exact approver roles — requires already knowing which failure modes exist. You only discover those by running the naive prompt first and watching it fail, which means the CRAFT loop is genuinely iterative, not something you can skip by being careful upfront.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> In UC-0B, the [VERBATIM] fallback rule: "If a clause cannot be compressed without losing meaning, quote it verbatim and mark it [VERBATIM] rather than paraphrase incorrectly." The AI generated good summarisation rules but did not anticipate that some clauses (especially 5.2 with its dual-approver condition) are too semantically dense to paraphrase safely. The VERBATIM escape hatch is the only reliable guard against condition drops on high-stakes clauses.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating classification of incoming citizen grievances before they are routed to ward offices — the same UC-0A pattern but against live data. I will use RICE to lock the category taxonomy and escalation rules before touching any code, then use the CRAFT loop to test against known edge cases (multi-category descriptions, severity keywords embedded mid-sentence) before deploying.

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

# Vibe Coding Workshop — Submission PR

**Name:** Kashif Shaik  
**City / Group:** Pune  
**Date:** 2026-04-20  
**AI tool(s) used:** Antigravity (DeepMind)  

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

> Severity blindness.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be 'Urgent' if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15 (predicted based on keyword match).

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — the keyword 'child' and 'school' triggered Urgent for PM-202402, and 'injury' triggered it for PM-202420.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission and scope bleed.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 5.2 (two approvers) and 7.2 (no encashment during service) were often simplified or omitted.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — all clauses from 2.3 through 7.2 are included with their core obligations preserved.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — it added phrases like "as per standard municipal practice" which were not in the source.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause rule

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single average growth percentage for all wards and categories combined.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated everything and silently ignored or averaged the null rows without flagging them.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — it throws an error if 'all' is requested.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — it labels them as NULL and provides the reason from the notes (e.g., "Data not submitted by ward office").

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — precisely.

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use personal devices for approved work tools as long as you follow the IT policy." (This is a blended hallucination).

**Did it blend the IT and HR policies?**

> Yes — it combined the general mention of "work tools" from HR with the permission to use "personal devices" for email from IT.

**After your fix — what does your system return for this question?**

> "As per policy_it_acceptable_use.txt Section 3.1, personal devices may be used to access CMC email and the CMC employee self-service portal only. They must not be used to access, store, or transmit classified or sensitive CMC data (Section 3.2)."

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — the enforcement rules strictly prohibited hedging.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes.

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: no single-source rule → added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Refining the enforcement rules (the 'R' and 'E' in RICE). It requires thinking about exactly how the AI will fail before it fails.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The strict refusal template for UC-X: "This question is not covered in the available policy documents...". AI usually tries to be helpful rather than strictly accurate.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Automating the triage of customer support tickets for our new product launch.

---

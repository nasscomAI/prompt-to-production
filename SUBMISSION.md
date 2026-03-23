# Vibe Coding Workshop — Submission PR

**Name:** Satyam Yadav  
**City / Group:** Pune / Kolkata  
**Date:** 2026-03-17  
**AI tool(s) used:** Antigravity  

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
> Hallucinated sub-categories and false confidence on ambiguity.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**
> "Category MUST be one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."

**How many rows in your results CSV match the answer key?**
> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**
> Yes - The keyword-based trigger in Enforcement Rule 2 successfully captured these signals.

**Your git commit message for UC-0A:**
> UC-0A Implementation: RICE-based classifier and city results

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
> Clause omission and obligation softening (especially around multi-party approvals).

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**
> Clause 5.2 (Department Head AND HR Director approval dropped to just "approval").

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**
> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**
> Yes - It added phrases like "as per standard organizational practice" which were not in the text.

**Your git commit message for UC-0B:**
> UC-0B Fix multi-condition drop: AI missed the dual-approver requirement in Clause 5.2 → Implemented strict RICE enforcement to ensure all conditions are preserved.

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**
> It returned a single city-wide growth percentage without detailing ward-wise breakdowns.

**Did it aggregate across all wards? Did it mention the 5 null rows?**
> Yes, it aggregated everything. No, it silently ignored the null rows in the calculation.

**After your fix — does your system refuse all-ward aggregation?**
> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**
> Yes — All 5 null rows are identified with reasons from the notes column.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**
> Yes

**Your git commit message for UC-0C:**
> UC-0C Fix silent null handling: AI failed to flag missing spend data and aggregated across wards → Implemented mandatory null reporting and formula transparency.

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*
> "Yes, you can use your personal phone for approved remote work tools and email according to HR and IT policy."

**Did it blend the IT and HR policies?**
> Yes, it combined the remote work allowance from HR with the phone access policy from IT.

**After your fix — what does your system return for this question?**
> "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Storing or transmitting classified CMC data is prohibited. Source: IT Policy Section 3.1"

**Did your system use any hedging phrases in any answer?**
> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**
> Yes

**Your git commit message for UC-X:**
> UC-X Fix hedged hallucination: AI blended policies and used vague language → Implemented zero-blending rule and exact refusal template.

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**
> Refining the enforcement rules was the hardest. It requires precisely predicting how the AI might "soften" or "hallucinate" information and creating explicit barriers against those specific tendencies.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**
> The explicit Refusal Protocol: "If a question is not covered, output exactly...". The AI usually tries to be helpful by guessing; forcing it to use a template is critical.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**
> Automating technical documentation reviews to ensure API security requirements are explicitly stated and never "softened" during generation.

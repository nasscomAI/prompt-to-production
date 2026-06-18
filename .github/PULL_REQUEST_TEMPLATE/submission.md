# Vibe Coding Workshop — Submission PR

**Name:** Meher Madhuri
**City / Group:** Hyderabad
**Date:** 2026-06-18
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
*severity blindness*

> Severity blindness was the primary failure where safety-critical complaints (containing keywords like 'ambulance', 'hospital', or 'school') were classified as Standard instead of Urgent.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> `- "Priority must be Urgent if description contains any of the following severity keywords (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"`

**How many rows in your results CSV match the answer key?**
*15* out of 15

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes, all severity signal rows (e.g. GH-202401 with 'ambulance', GH-202411 with 'hospital', GH-202412 with 'school', and GH-202422 with 'collapsed') returned Urgent.

**Your git commit message for UC-0A:**

> `UC-0A Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers`

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*clause omission*

> The naive summary omitted multiple key clauses and dropped critical details from multi-condition clauses.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clauses 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2. Especially Clause 5.2 was weakened by dropping the requirement of dual approval from both the Department Head and HR Director.

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes, all 10 clauses are present and fully detailed in `summary_hr_leave.txt`.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes, the naive summary often introduced standard office practices or general advice not found in the original policy document.

**Your git commit message for UC-0B:**

> `UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause rule`

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> It returned a single aggregated YoY/MoM growth percentage across all wards and categories combined, without mentioning or handling the null values.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across all wards, and did not mention or handle the 5 null rows (silently ignored/skipped them).

**After your fix — does your system refuse all-ward aggregation?**

> Yes.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes. Null rows are detected during loading, printed to stdout with their original notes, and listed as NULL in the output file with their original notes.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes.

**Your git commit message for UC-0C:**

> `UC-0C Fix silent aggregation: no ward/category scope → enforced per-ward per-category only`

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> It returned a blended answer stating that personal devices can access CMC email, the self-service portal, and approved remote work tools, incorrectly merging IT policy restrictions with HR policy mentions of remote tools.

**Did it blend the IT and HR policies?**

> Yes, it blended them.

**After your fix — what does your system return for this question?**

> `According to Clause 3.1 of policy_it_acceptable_use.txt, personal devices may be used to access CMC email and the CMC employee self-service portal only. Clause 3.2 specifies that personal devices must not be used to access, store, or transmit classified or sensitive CMC data. Source: policy_it_acceptable_use.txt Section 3.1, 3.2`

**Did your system use any hedging phrases in any answer?**
*(example: "while not explicitly covered", "typically", "generally understood")*

> No, it did not.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes, all 7 test questions produced either a single-source cited answer or the exact refusal template.

**Your git commit message for UC-X:**

> `UC-X Fix cross-doc blending: no single-source rule → added single-source attribution enforcement`

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Analyze step was the most challenging because it required tracing how subtle variations in query phrasing or keyword patterns caused the AI model/retrieval engine to either bypass constraints or cross-contaminate sources.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The precise refusal template for UC-X: 'This question is not covered in the available policy documents...' which forces a strict structural constraint preventing hedged hallucinations.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Standardizing and automating our customer support classification ticket routing using deterministic safety-critical triggers and guardrails.

# Vibe Coding Workshop — Submission PR

**Name:** Srikanth Bhukya
**City :** Hyderabad
**Date:** April 2, 2026
**AI tool(s) used:** Antigravity (Agentic AI)

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
> missing justification / unmapped placeholders

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**
> "Priority must be Urgent if description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse. Otherwise Standard."

**How many rows in your results CSV match the answer key?**
> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**
> Yes — The Python logic deterministically checks against an array of urgent keywords, forcing priority escalation over defaults.

**Your git commit message for UC-0A:**
> UC-0A Fix unimplemented logic: missing classification schema -> implemented explicit category and urgent priority

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
> clause omission / obligation softening

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**
> Clause 5.2 (Condition dropping: dropping the dual-approval requirement of both Department Head AND HR Director)

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**
> Yes — All 10 clauses are natively parsed by regex and securely mapped line-by-line avoiding LLM hallucinated omissions.

**Did the naive prompt add any information not in the source document (scope bleed)?**
> No — My parser quotes the explicit document constraint verbatim.

**Your git commit message for UC-0B:**
> UC-0B Fix clause omission: completeness not enforced -> added verbatim extraction of 10 required numbered clauses

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**
> It refused to run without proper scoped arguments, avoiding the failure mode.

**Did it aggregate across all wards? Did it mention the 5 null rows?**
> No, it strictly demands cross-ward granular filtering.

**After your fix — does your system refuse all-ward aggregation?**
> Yes. It contains an abort if `--ward` and `--category` slices are not explicitly passed.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**
> Yes — They are explicitly replaced with: FLAGGED NULL: <verbatim text from notes column>.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**
> Yes. The pure mathematical loop guarantees isolated MoM precision matching exactly +33.1% (without fabricating the missing notes).

**Your git commit message for UC-0C:**
> UC-0C Fix silent aggregation: no scope in enforcement -> restricted to per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
> Refusal prompt / Native IT permission depending on iteration.

**Did it blend the IT and HR policies?**
> No — The logic enforces deterministic returns, physically separating HR leave paths from IT acceptable use limits.

**After your fix — what does your system return for this question?**
> "Personal devices may be used to access CMC email and the CMC employee self-service portal only. They must not be used to access, store, or transmit classified or sensitive CMC data. (Source: policy_it_acceptable_use.txt, Section 3.1 and 3.2)"

**Did your system use any hedging phrases in any answer?**
> No.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**
> Yes.

**Your git commit message for UC-X:**
> UC-X Fix cross-doc blending: no single-source rule -> added single-source attribution enforcement

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**
> Enforcing absolute determinism in UC-X without the agent guessing between interconnected documents. It required enforcing explicit boundaries so the system couldn't guess unwritten policy permissions. 

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**
> "If the exact answer is not physically written in the documents, unconditionally supply the exact refusal template [...] with no variations."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**
> Converting un-structured log analysis reports into deterministic compliance summaries.

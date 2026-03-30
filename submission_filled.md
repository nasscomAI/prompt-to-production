# Vibe Coding Workshop — Submission PR

**Name:** Darshan Prajapati
**City / Group:** Ahmedabad
**Date:** 2026-03-30
**AI tool(s) used:** Antigravity (Google DeepMind)

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_ahmedabad.csv` without crash
- [x] `results_ahmedabad.csv` present in `uc-0a/`
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

> "Priority must be 'Urgent' if the description contains any of the following keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — AM-202407 containing 'child' correctly returned Urgent even without a clear category.

**Your git commit message for UC-0A:**

> UC-0A Fix severity blindness: no keywords in enforcement → added injury/child/school/hospital triggers

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> clause omission

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Clause 5.2 (requires BOTH Department Head AND HR Director approval) was simplified to "requires manager approval".

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — "as is standard practice in government organizations".

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause rule

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> "The overall budget growth for the city is approximately 12.5% across all wards."

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, it aggregated across wards and silently ignored the null rows in the average.

**After your fix — does your system refuse all-ward aggregation?**

> Yes

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — the internal logic flags the 5 null rows and refuses to compute growth for them (e.g., Ward 4 Roads in July 2024).

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category only

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, you can use personal devices for work if approved by your manager, and you may be eligible for a phone reimbursement." (Blended IT and HR/Finance policies incorrectly).

**Did it blend the IT and HR policies?**

> Yes

**After your fix — what does your system return for this question?**

> "Personal devices must not be connected to the CMC internal network (wired or wireless). The CMC Guest WiFi network is available for personal device internet access. Source: policy_it_acceptable_use.txt Section 3.3"

**Did your system use any hedging phrases in any answer?**

> No

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: improved scoring logic → added phrase-level weighting and stricter refusal threshold

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> The Refine step was the hardest because it required finding the exact balance between strict enforcement and helpful answers, especially when dealing with ambiguous cases like "personal phone" vs "home office equipment".

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The explicit refusal template: "This question is not covered in the available policy documents...". The AI tended to try and be "helpful" by guessing from partial information instead of refusing.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> I will use RICE to define strict boundaries for our customer support bot to ensure it doesn't promise refunds outside of the official warranty document.

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

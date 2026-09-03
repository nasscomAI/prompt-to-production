# Vibe Coding Workshop — Submission PR

**Name:** Sneha
**City / Group:** Amritsar (Pune dataset validated)
**Date:** 2026-09-03
**AI tool(s) used:** Muse Spark (Opencode) + manual CRAFT

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_[city].csv` without crash
- [x] `results_[city].csv` present in `uc-0a/` (pune + hyderabad + kolkata + ahmedabad verified, 15 rows each)
- [x] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/` (29 clauses, 38 lines)
- [x] `growth_output.csv` present in `uc-0c/` (12 periods, Ward 1 – Kasba Roads MoM)
- [x] 4+ commits with meaningful messages following the formula (5 commits on participant/Sneha-Amritsar)
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**
*(taxonomy drift / severity blindness / missing justification / hallucinated sub-categories / false confidence)*

> Taxonomy drift + severity blindness + missing justification. Naive `Classify this citizen complaint` returned `Water Damage` (not in allowed list, correct is `Heritage Damage`), missed `injury/child/school/hazard/fell` → Standard instead of Urgent, and left `reason` empty on ambiguous rows.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations, no Water Damage."

**How many rows in your results CSV match the answer key?**
*(Tutor will release answer key after session)*

> 15 out of 15 — taxonomy PASS on 4 cities (60 rows total: Pune 4 Urgent, Hyderabad 4 Urgent, Kolkata 1 Urgent, Ahmedabad 1 Urgent), every row has reason citing matched keyword.

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — PM-202402 `child, school` → Urgent, PM-202411 `hazard` → Urgent, PM-202420 `injury` → Urgent, PM-202446 `fell` → Urgent, GH-202401 `ambulance` → Urgent, GH-202411 `hospital` → Urgent, GH-202412 `school` → Urgent, KM-202421 `hospital, fell` → Urgent, AM-202407 `child` → Urgent. No exceptions.

**Your git commit message for UC-0A:**

> UC-0A Fix taxonomy drift: Water Damage → Heritage Damage + urgent + reason → verified on 4 cities

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**
*(clause omission / scope bleed / obligation softening)*

> Clause omission + obligation softening + scope bleed. Naive `Summarize the policy document.` omitted 2.5, dropped second condition in 5.2 (kept "requires approval" but lost "Department Head AND HR Director"), and added bleed.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Missing: 2.5 LOP regardless, 5.2 second approver, 7.2 not permitted. Weakened: 2.4 lost "Verbal not valid", 2.6 lost "forfeited on 31 December", 3.4 lost "regardless of duration", 5.3 lost "Municipal Commissioner".

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes — 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2 all present verbatim flagged [VERBATIM], plus all 1.1–8.2 (29 clauses).

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — "as is standard practice", "typically in government organisations", "employees are generally expected to" — none in policy_hr_leave.txt.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission: completeness not enforced → added every-numbered-clause + verbatim for 10 critical

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> Single aggregated number for all wards combined (e.g., "Overall growth 12.3%") with no ward/category breakdown, no formula, guessed MoM without asking.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes, aggregated across 5 wards/5 categories. No — 5 nulls (2024-03 Shivajinagar Drainage, 2024-07 Warje Roads, 2024-11 Kasba Waste, 2024-08 Kothrud Parks, 2024-05 Hadapsar Streetlight) were silently skipped, no notes copied.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — `REFUSAL: Aggregation across wards/categories not allowed — specify single --ward and single --category.` exit 2, lists available wards/categories.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes — load_dataset logs 5 nulls before compute; e.g., 2024-03 Ward 2 – Shivajinagar Drainage → `NULL: flagged — Data not submitted by ward office`; growth_output.csv shows formula per row.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — Ward 1 – Kasba Roads & Pothole Repair: 2024-07 19.7 `MoM: (19.7-14.8)/14.8*100=+33.1%` (monsoon spike), 2024-10 13.1 `MoM: (13.1-20.1)/20.1*100=-34.8%` (post-monsoon). 12 periods, formula every row.

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation: no scope in enforcement → restricted to per-ward per-category + flag nulls + formula

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**
*(Question: "Can I use my personal phone to access work files when working from home?")*

> "Yes, personal phones can be used for approved remote work tools and email." — blended IT 3.1 (email+portal only) with HR remote-work mention.

**Did it blend the IT and HR policies?**

> Yes — combined IT policy 3.1 and HR approved tools into permission that does not exist in either document.

**After your fix — what does your system return for this question?**

> "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Source: policy_it_acceptable_use.txt Section 3.1" — single-source, no HR blending.

**Did your system use any hedging phrases in any answer?**
*("while not explicitly covered", "typically", "generally understood")*

> No — BANNED_PHRASES filtered; no answer contains "while not explicitly covered", "typically", "generally understood", "it is common practice".

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — 7/7: 1) HR 2.6 `5 days forfeited 31 Dec` + citation, 2) IT 2.3 `written IT approval`, 3) Finance 3.1 `Rs 8,000 one-time permanent WFH`, 4) trap IT 3.1 single-source, 5) `This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.` exact, 6) Finance 2.6 `cannot be claimed simultaneously`, 7) HR 5.2 `Department Head AND HR Director`.

**Your git commit message for UC-X:**

> UC-X Fix cross-doc blending: no single-source rule → added single-source attribution + exact refusal template

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Reflect — testing the naive prompt first revealed subtle failures (heritage zone garbage → Waste not Heritage, road+temperature → Heat not Road) that weren’t obvious until running on all 4 cities/budget nulls. Fixing required precedence tuning, not just keyword addition.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> UC-0A: "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations, no Water Damage." — AI drafted generic list with Water Damage; manual fix to Heritage Damage prevented taxonomy drift.

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Summarizing client meeting notes into Jira tickets — will write RICE (role: ticket writer, intent: verifiable acceptance criteria), agents.md enforcement (every ticket must have Component + Estimate), then CRAFT loop with AI draft + test on 5 past meetings.

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

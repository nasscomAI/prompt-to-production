# Vibe Coding Workshop — Submission PR

**Name:** Soham Ghatpande  
**City / Group:** Pune  
**Date:** 2026-08-14  
**AI tool(s) used:** Cursor  

---

## Checklist — Complete Before Opening This PR

- [x] `agents.md` committed for all 4 UCs
- [x] `skills.md` committed for all 4 UCs
- [x] `classifier.py` runs on `test_[city].csv` without crash
- [x] `results_[city].csv` present in `uc-0a/` (`results_pune.csv`)
- [x] `app.py` for UC-0B, UC-0C, UC-X — all run without crash
- [x] `summary_hr_leave.txt` present in `uc-0b/`
- [x] `growth_output.csv` present in `uc-0c/`
- [x] 4+ commits with meaningful messages following the formula
- [x] All sections below are filled in

---

## UC-0A — Complaint Classifier

**Which failure mode did you encounter first?**

> Taxonomy drift and severity blindness. A naive "classify this complaint" prompt reworded/pluralised categories (e.g. "Potholes", "Street Lights") and rated injury/child/school complaints as Standard instead of Urgent.

**What enforcement rule fixed it? Quote the rule exactly as it appears in your agents.md:**

> "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive word match)." — together with: "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations or invented labels."

**How many rows in your results CSV match the answer key?**

> Answer key not yet released. `results_pune.csv` classifies all 15 rows with the enforced taxonomy, and every severity-signal row is Urgent.

**Did all severity signal rows (injury/child/school/hospital) return Urgent?**

> Yes — the severity-keyword rule forces Urgent whenever any listed keyword appears (including related forms such as "children" mapped to the child signal). Examples: PM-202402 (school/child), PM-202411 (hazard), PM-202420 (injury), PM-202446 (fell).

**Your git commit message for UC-0A:**

> UC-0A Fix taxonomy drift and severity blindness: naive prompt reworded categories and missed Urgent signals → added verbatim taxonomy, severity-keyword Urgent rule, reason citations and NEEDS_REVIEW in agents.md with rule-based classifier + results_pune.csv

---

## UC-0B — Summary That Changes Meaning

**Which failure mode did you encounter?**

> All three — clause omission, obligation softening, and scope bleed. The naive summary dropped low-salience numbered clauses, downgraded "must/requires/not permitted" to "should/generally", and added phrases like "as is standard practice" not in the source.

**List any clauses that were missing or weakened in the naive output (before your RICE fix):**

> Most at risk: 5.2 (dropped the second approver — kept "requires approval" but lost "Department Head AND HR Director"), 2.6/2.7 (carry-forward limit and forfeiture date dropped), 3.4 (cert-before/after-holiday condition dropped), 7.2 ("not permitted" softened).

**After your fix — are all 10 critical clauses present in summary_hr_leave.txt?**

> Yes. The summariser retains every required binding clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) with required tokens checked in code; 5.2 keeps BOTH Department Head and HR Director. Run result: PASS.

**Did the naive prompt add any information not in the source document (scope bleed)?**

> Yes — the classic bleed phrases ("as is standard practice", "typically in government organisations", "employees are generally expected to"). The fix bans them and only emits source text.

**Your git commit message for UC-0B:**

> UC-0B Fix clause omission and obligation softening: naive summary dropped clauses and weakened must/requires → enforced every-clause completeness, multi-condition preservation (5.2 both approvers), no scope bleed; summariser writes summary_hr_leave.txt

---

## UC-0C — Number That Looks Right

**What did the naive prompt return when you ran "Calculate growth from the data."?**

> A single blended growth number for all wards and categories combined, with no ward/category breakdown, no formula shown, and no mention of the missing values.

**Did it aggregate across all wards? Did it mention the 5 null rows?**

> Yes it aggregated across all wards (wrong level), and no — it silently ignored the 5 null actual_spend rows.

**After your fix — does your system refuse all-ward aggregation?**

> Yes — the tool operates on ONE ward + ONE category and raises a REFUSE message if `--ward`/`--category` is missing or set to all-ward aggregation.

**Does your growth_output.csv flag the 5 null rows rather than skipping them?**

> Yes. `load_dataset` reports all 5 nulls up front with their notes reason (2024-03 Ward 2 Drainage, 2024-05 Ward 5 Streetlight, 2024-07 Ward 4 Roads, 2024-08 Ward 3 Parks, 2024-11 Ward 1 Waste). Null current/prior values are flagged (`NULL_ACTUAL_SPEND`), never computed through.

**Does your output match the reference values (Ward 1 Roads +33.1% in July, −34.8% in October)?**

> Yes — `growth_output.csv` shows 2024-07 = +33.1% and 2024-10 = −34.8% for Ward 1 – Kasba / Roads & Pothole Repair, with the MoM formula printed per row.

**Your git commit message for UC-0C:**

> UC-0C Fix silent aggregation and null skipping: naive prompt aggregated across wards and hid null rows → restricted to per-ward per-category scope, flagged all 5 null rows with reasons, required explicit --growth-type and printed formula per row (growth_output.csv)

---

## UC-X — Ask My Documents

**What did the naive prompt return for the cross-document test question?**

> The naive approach blended IT and HR into a permissive answer like "Yes, personal phones can be used for approved remote work tools and email" — a permission in neither document.

**Did it blend the IT and HR policies?**

> Yes — it combined IT §3.1 (personal devices → email + portal only) with a vague HR remote-work notion to manufacture broader permission.

**After your fix — what does your system return for this question?**

> Single-source IT answer, no blend:  
> Source: policy_it_acceptable_use.txt, section 3.1  
> Personal devices may be used to access CMC email and the CMC employee self-service portal only.  
> (Plus same-document 3.2 when work-files/sensitive access is implied — still IT only, never HR.)

**Did your system use any hedging phrases in any answer?**

> No. The system only returns a verbatim cited clause or the exact refusal template, so hedging phrases cannot appear.

**Did all 7 test questions produce either a single-source cited answer or the exact refusal template?**

> Yes — verified on all 7: Q1→HR 2.6, Q2→IT 2.3, Q3→Finance 3.1, Q4→IT 3.1 (single-source, no blend), Q5→refusal template, Q6→Finance 2.6, Q7→HR 5.2 (Department Head AND HR Director).

**Your git commit message for UC-X:**

> UC-X Fix cross-document blending and hedged hallucination: naive prompt blended IT/HR and hedged → enforced single-source retrieval with document+section citations, exact refusal template and personal-phone IT-only routing; verified on all 7 test questions

---

## CRAFT Loop Reflection

**Which CRAFT step was hardest across all UCs, and why?**

> Writing testable Enforcement rules. Stating intent was easy; turning each failure mode into a machine-checkable rule — e.g. "preserve BOTH approvers in clause 5.2" or "never blend IT and HR on personal-device questions" — was the hard part, and exactly where the naive prompt fails silently.

**What is the single most important thing you added manually to an agents.md that the AI did not generate on its own?**

> The multi-condition preservation rule in UC-0B: "Multi-condition obligations must preserve ALL conditions — never drop one silently (e.g. clause 5.2 must retain both Department Head and HR Director; keeping only 'requires approval' is a condition drop)."

**Name one real task in your work where you will apply RICE + CRAFT within the next two weeks:**

> Drafting an internal SOP summariser that must preserve mandatory approval steps and escalation thresholds verbatim — applying the same completeness + condition-preservation enforcement so no compliance step is silently softened.

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

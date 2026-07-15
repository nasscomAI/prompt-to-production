# Agents for UC-0A — Complaint Classifier (R.I.C.E)

This document summarizes the agents used by `uc-0a` and prioritizes them using the R.I.C.E framework (Reach · Impact · Confidence · Effort). It is derived from the `README.md` requirements and the skills defined in `skills.md`.

## 1) `classify_complaint` (core inference agent)
- Reach: All individual complaint rows in each input CSV (100% of rows processed by the pipeline).
- Impact: High — produces the `category`, `priority`, `reason`, and `flag` fields required by the output schema; directly affects correctness and downstream decisions.
- Confidence: Medium–High — deterministic schema and severity keywords raise confidence, but natural-language ambiguity and hallucination risks remain.
- Effort: Medium — requires careful prompt design, justification extraction, and strict enforcement of allowed category strings.

Notes: Enforce exact `category` strings, apply severity keywords to set `priority` to `Urgent`, and include a one-sentence `reason` citing text from the description.

## 2) `batch_classify` (batch orchestration agent)
- Reach: Entire input CSV files (runs the `classify_complaint` agent over all rows).
- Impact: High — operationalizes the classifier for end-to-end runs and produces `uc-0a/results_[city].csv` files.
- Confidence: High — straightforward orchestration; failures are primarily from the `classify_complaint` agent.
- Effort: Low — mainly I/O, batching, error handling, and retries.

Notes: Implement graceful handling for rows flagged `NEEDS_REVIEW` and ensure outputs match the required CSV schema exactly.

## 3) `schema_enforcer` (validation & sanitizer agent)
- Reach: All outputs before they are written to disk (post-classification validation of each row).
- Impact: High — prevents invalid category values, missing `reason`, or incorrect `priority` labels from reaching results.
- Confidence: High — rule-based checks are deterministic and simple to validate.
- Effort: Low–Medium — implement value checks, severity-keyword verification, and reason presence rules.

Notes: This agent should auto-correct trivial deviations (trim/normalize spacing) and mark genuinely ambiguous or unfixable rows with `flag=NEEDS_REVIEW`.

## 4) `human_reviewer` (human-in-the-loop fallback)
- Reach: Only rows where `flag=NEEDS_REVIEW` (expected minority of cases).
- Impact: Medium — resolves ambiguity, reduces false confidence, and supplies labeled examples for future prompt improvements.
- Confidence: Very High for reviewed rows (humans resolve edge cases reliably).
- Effort: Low (per-row) but scales with review volume; requires UI or simple CSV review process.

Notes: Capture reviewer rationale in a separate column to help prompt tuning and model audits.

## 5) `prompt_tuner` (improvement & monitoring agent)
- Reach: Model prompts and few-shot examples used by `classify_complaint` across cities and batches.
- Impact: High — reduces taxonomy drift, hallucination, and severity-misclassification when effective.
- Confidence: Medium — improvements depend on quality of examples and testing across failure modes.
- Effort: High — iterative evaluation, A/B testing on held-out city files, and incorporating reviewer feedback.

Notes: Maintain a small test-suite (city test CSVs in `../data/city-test-files`) and log failure-mode metrics defined in `README.md` to measure improvements.

---

Recommended next steps
- Implement `schema_enforcer` as a lightweight pre-write validator (quick wins).
- Improve `classify_complaint` prompts to require an explicit citation for `reason` and to return exact category strings only.
- Wire flagged rows to a simple `human_reviewer` CSV workflow and collect reviewer rationales for prompt tuning.

If you want, I can implement `agents.md` changes into the repository, add a simple `schema_enforcer.py` prototype, or open a PR with these changes.
## Agent specification (Role, Intent, Context, Enforcement)

role: >
  Automated single-row classification agent used inside the UC-0A pipeline. It
  receives one complaint record (CSV row) and must output exactly the fields
  `category`, `priority`, `reason`, and `flag`. The agent operates only on the
  supplied row data and any in-repo test examples — it MUST NOT perform any
  external network lookups or use out-of-band resources.

intent: >
  Produce a correct, verifiable classification for the input complaint where:
  - `category` is one of the allowed exact strings.
  - `priority` is `Urgent`, `Standard`, or `Low` and follows severity rules.
  - `reason` is a one-sentence justification that cites specific words from
    the complaint description.
  - `flag` is `NEEDS_REVIEW` only for genuinely ambiguous or unresolvable
    cases; otherwise `flag` is blank.

context: >
  Allowed inputs: the complaint `description` and any other columns present in
  the same CSV row (e.g., location, timestamp). Also allowed: the list of
  permitted `category` values and the severity keyword list defined in
  `README.md`. Disallowed: web searches, external databases, guessing facts not
  present in the row, or inventing sub-categories not in the allowed list.

enforcement:
  - "Category must be exactly one of: Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other"
  - "If description contains any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse), then `priority` must be `Urgent`."
  - "`reason` must be one sentence and include at least one exact word or short phrase taken from the description (e.g., cite 'leaking manhole' or 'child injured')."
  - "If category cannot be determined unambiguously from the description, set `category` to `Other` and `flag` to `NEEDS_REVIEW` (do not fabricate justification)."
  - "Trim and normalize whitespace, but do not alter category spelling or capitalization beyond the exact allowed strings."
  - "If the description is empty or missing, set `category` to `Other`, `priority` blank, `reason` to 'No description provided', and `flag` to `NEEDS_REVIEW`."
  - "Output must include all four fields (`category`,`priority`,`reason`,`flag`) for every row; `flag` may be blank but must exist."


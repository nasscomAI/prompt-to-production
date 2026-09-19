# Session README — Vibe Coding Workshop (Civic Tech Edition)

Participant branch: `participant/participant-pune` (city: **Pune**)

This file is the participant's session log. It does not replace the workshop
`README.md` — it documents what was built, how to run each piece, and progress
across the four use cases.

---

## Repo status

| UC | Deliverable | Status |
|----|-------------|--------|
| UC-0A | Complaint Classifier | ✅ Built · `results_[city].csv` produced for all 4 cities |
| UC-0B | Summary That Changes Meaning | ✅ Built · `summary_hr_leave.txt` produced |
| UC-0C | Number That Looks Right | ✅ Built · `growth_output.csv` produced |
| UC-X | Ask My Documents | ✅ Built · all 7 test questions pass |

Data files confirmed present:
`data/city-test-files/`, `data/policy-documents/`, `data/budget/ward_budget.csv`.

Environment: Python 3.14.7 · Git 2.55.0 · `csv`/`json` import OK.

---

## UC-0A — Complaint Classifier

Files:
- `uc-0a/agents.md` — RICE spec (role, intent, context, enforcement)
- `uc-0a/skills.md` — `classify_complaint` + `batch_classify`
- `uc-0a/classifier.py` — implementation
- `uc-0a/results_pune.csv` — generated output (15 rows)
  plus `results_hyderabad.csv`, `results_kolkata.csv`, `results_ahmedabad.csv`

**How to run:**
```bash
cd uc-0a
python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
```

**Classification rules (enforced):**
- `category` — exact strings only: Pothole · Flooding · Streetlight · Waste ·
  Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other
- `priority` — `Urgent` iff a severity keyword is present
  (`injury, child, school, hospital, ambulance, fire, hazard, fell, collapse`);
  `Low` only for minor markers; otherwise `Standard`
- `reason` — one sentence quoting the exact words that drove the decision
- `flag` — `NEEDS_REVIEW` on genuine ambiguity (category tie, no match, or
  heritage-context streetlight complaints), otherwise blank

**CRAFT loop — what failed on the naive prompt → what changed:**
- *False confidence on ambiguity:* the heritage-street complaint (PM-202430,
  "Heritage street, lights out") was classified confidently with no flag.
  → Added heritage-context conflict detection; it now yields `Streetlight` +
  `NEEDS_REVIEW`.
- *Category tie blindness:* flooding + drain-blocked complaints were resolved
  without any review marker. → Ties now force `NEEDS_REVIEW`.
- *Severity blindness:* priority was detached from severity keywords.
  → Priority is now strictly a function of the severity keyword list.

**Verification:** a rule-checker (categories, priorities, urgent-trigger
consistency, reason presence, flag validity) passes all 15 rows with 0 errors.

---

## UC-0B — Summary That Changes Meaning

Files:
- `uc-0b/agents.md` — RICE spec
- `uc-0b/skills.md` — `retrieve_policy` + `summarize_policy`
- `uc-0b/app.py` — implementation
- `uc-0b/summary_hr_leave.txt` — generated output (all 29 clauses)

**How to run:**
```bash
cd uc-0b
python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
```

**Enforcement (verified):**
- Clause coverage — every numbered clause (1.1–8.2 = 29) must appear in output; missing summaries raise a fatal error
- Condition preservation — per-clause token check (timeframes, approvers, amounts, prohibitions) fails → clause written verbatim and flagged `[VERBATIM]`
- No invented info — scope-bleed phrases (`as is standard practice`, `typically in government`, ...) are detected and refused
- Binding verbs (`must`/`will`/`requires`/`not permitted`) are never softened

**Verification:** checker confirms 29/29 source clauses present, zero extra
clauses, zero scope-bleed phrases, zero `[VERBATIM]` fallbacks needed, and no
softened binding verbs.

**CRAFT loop — what failed on the naive prompt → what changed:**
- *Clause omission:* the first section parser rejected `5. LEAVE WITHOUT PAY (LWP)`
  because the title regex only allowed letters — sections 5.1–5.4 were silently
  dropped (25 of 29 clauses). → Broadened the title regex to allow parentheses
  and digits; coverage now forces all 29 clauses.
- *Condition dropping:* a plain rephrase could drop "Department Head AND HR
  Director" or "within 48 hours". → Added a token-preservation pass that proves
  every mandatory condition survived; violations are quoted verbatim with
  `[VERBATIM]` instead of silently weakening.

---

## UC-0C — Number That Looks Right

Files:
- `uc-0c/agents.md` — RICE spec (role, intent, context, enforcement)
- `uc-0c/skills.md` — `load_dataset` + `compute_growth`
- `uc-0c/app.py` — implementation
- `uc-0c/growth_output.csv` — generated output (Ward 1 – Kasba / Roads &
  Pothole Repair plus the 5 (ward, category) pairs that contain a null row)

**How to run:**
```bash
cd uc-0c
python app.py --input ../data/budget/ward_budget.csv \
  --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" \
  --growth-type MoM --output growth_output.csv
```

**Enforcement (verified, refusals run before any computation):**
- Per-ward per-category only — `--ward` and `--category` are repeatable and
  paired positionally; a missing `--growth-type`, `--ward`/`--category`, or any
  aggregate word (`all`, `total`, `combined`, `every`, ...) is refused with
  exit code 2
- Unknown ward/category names are refused with a list of valid alternatives
- Every null `actual_spend` row is `NULL_FLAGGED` with its notes reason; the
  following month is `PRIOR_NULL_FLAGGED` instead of being computed against a gap
- The growth formula is shown in every output row alongside the result
- Status column: `OK` | `NULL_FLAGGED` | `PRIOR_NULL_FLAGGED` |
  `NO_PRIOR_PERIOD` | `DIVIDE_BY_ZERO`

**Verification:** reference values reproduce — Ward 1 – Kasba / Roads &
Pothole Repair 2024-07 `(19.7 - 14.8) / 14.8 = +33.1%`, 2024-10
`(13.1 - 20.1) / 20.1 = -34.8%`. All 5 null rows flagged; the period after each
null is `PRIOR_NULL_FLAGGED`; `--ward all` and missing `--growth-type` both
exit 2 with a refusal message.

**CRAFT loop — what failed on the naive prompt → what changed:**
- *Silent aggregation:* a naive sum across all wards looks coherent and hides
  the 5 empty cells — a naive result treats those blanks as zero, which turns
  neighbouring months into fake spikes and drops. → Aggregation is refused
  outright; growth is only ever computed per explicit (ward, category) pair.
- *Null skipping:* a naive loop computes around blank cells and never mentions
  them. → `load_dataset` reports the 5 null rows up front, null rows carry the
  notes reason, and the month after a null is flagged `PRIOR_NULL_FLAGGED`.
- *Formula guessing:* MoM vs YoY changes every number. → `--growth-type` is
  required; the formula is printed per row so the reader can verify it.

---

## UC-X — Ask My Documents

Files:
- `uc-x/agents.md` — RICE spec (role, intent, context, enforcement)
- `uc-x/skills.md` — `retrieve_documents` + `answer_question`
- `uc-x/app.py` — implementation (interactive CLI + `--ask "..."`)

**How to run:**
```bash
cd uc-x
python app.py                          # interactive
python app.py --ask "Who approves leave without pay?"
```

**How it works:**
- `retrieve_documents` parses all three policy files into clauses and builds
  an IDF table over clause tokens (rare words carry more evidence)
- `answer_question` scores clauses with one-word-one-term matching: an exact
  match counts in full, a synonym match half, and each clause word backs only
  one question term (so `device` cannot count for both `mobile` and `phone`)
- Single-source rule — every quoted clause in an answer comes from the same
  document, cited as `Source: <doc> - section <n>`; a rival clause from
  another document scoring within 90% of the best triggers the refusal
  template instead of a blend
- Refusal template returned verbatim for uncovered questions; a built answer
  is asserted free of hedging phrases

**Enforcement (verified):** never combines claims across documents; never
uses hedging phrases (`while not explicitly covered`, `typically`,
`generally understood`, `it is common practice`); uncovered questions use the
exact refusal template; every factual claim cites document + section.

**Verification — all 7 README test questions:**
- Carry forward → HR 2.6 · Slack install → IT 2.3 · Home office allowance →
  Finance 3.1 · Personal phone from home → IT 3.1 + 3.2 (single source, NOT
  blended) · Flexible working culture → refusal template · DA + meal receipts
  same day → Finance 2.5 + 2.6 (simultaneous claim prohibited) · Leave without
  pay approval → HR 5.2 + 5.3 (Department Head AND HR Director)

**CRAFT loop — what failed on the naive prompt → what changed:**
- *Cross-document blending:* the personal-phone question tempted a blend of
  "personal devices (IT 3.1)" with anything mentioning approved remote work.
  → The single-document rule plus the 90% rival-document refusal threshold
  make a blend structurally impossible.
- *Shared-word bleed:* a lone word like `home` or `device` could drag in a
  wrong clause. → Synonym matches count at half weight, one clause word backs
  one question term only, and a best clause with fewer than 2 distinct
  non-generic evidence terms is refused.
- *Hedged hallucination:* without a required output format the model drifts to
  "while not explicitly covered...". → The exact refusal template is wired in
  and every built answer is asserted free of hedging phrases.

---

## Commit log (workshop formula)

Every change below follows the official formula:
`[UC-ID] Fix [what]: [why it failed] → [what you changed]`

```
[UC-0A] Fix ambiguity blindness: heritage-context and category ties were
classified with false confidence → added NEEDS_REVIEW flagging + strict
severity keyword enforcement

[UC-0A] Fix missing city coverage: only Pune output existed → ran the
classifier on Hyderabad, Kolkata, and Ahmedabad test files; all rows pass
the rule check

[UC-0A] Fix session log: commit history not documented in README → added
commit log section using the workshop formula with both change entries

[UC-0B] Fix clause omission: section-title regex rejected "(LWP)" so
sections 5.1-5.4 were silently dropped → broadened the regex and added a
29-clause coverage check plus a per-clause token-preservation pass
(conditions dropped → verbatim + [VERBATIM] flag)

[UC-0C] Fix silent aggregation + null skipping: a single all-ward number hid
the 5 blank actual_spend rows and treated them as zero → per-ward per-category
only (aggregate words refused, exit 2), null rows flagged with their notes
reason and PRIOR_NULL_FLAGGED after each gap, --growth-type required, formula
shown per row

[UC-X] Fix cross-document blending on the personal-phone question: shared words
let IT/Finance clauses outrank the real answer → clause index with IDF scoring,
one-word-one-term matching, single-document answers with section citations,
rival-document tie (within 90%) → exact refusal template, hedging phrases
blocked
```
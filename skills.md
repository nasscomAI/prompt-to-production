# UC-0B: Summary That Changes Meaning — skills.md

## Skill 1: Clause-Complete Summarisation

**What it does:**
Reads a policy document and produces a summary that contains every numbered clause, preserving the original section order.

**Trigger condition:**
Input is a `.txt` policy document with numbered sections (e.g. 1., 2.1, 3.2(b)).

**Implementation:**
- Extract all numbered headings/clauses using regex before summarising
- After summarisation, run a completeness check: every extracted clause number must appear in the output
- If a clause is missing, re-prompt with: "You omitted clause [X]. Add it now without changing any other content."

---

## Skill 2: Modal Verb Preservation

**What it does:**
Ensures that obligation words (`must`, `shall`, `will`, `is required to`) and prohibition words (`must not`, `may not`, `is not permitted`) are never weakened in the summary.

**Trigger condition:**
Any sentence in the source containing `must`, `shall`, `may not`, `is not permitted`, `is required`, `is prohibited`.

**Implementation:**
- After generating the summary, scan source for all modal-obligation phrases
- For each one, verify the summary contains an equivalent phrase with equal or stronger obligation
- Flag and re-generate any sentence where strength was downgraded

---

## Skill 3: Critical Clause Flagging

**What it does:**
Labels any summarised clause that contains a penalty, an eligibility condition, or an exception with the tag `[CRITICAL]`.

**Trigger condition:**
Source clause contains words like: `penalty`, `termination`, `not eligible`, `exception`, `unless`, `provided that`, `subject to`, `forfeit`, `disciplinary`.

**Implementation:**
- Scan source for trigger words before summarisation
- After summarisation, verify each such clause carries `[CRITICAL]` in the output
- If missing, append `[CRITICAL]` and a one-line reason

---

## Skill 4: File I/O and Output Validation

**What it does:**
Reads the input `.txt` document, calls the summarisation pipeline, and writes the output to `summary_[input_filename].txt`.

**Trigger condition:**
Script is run with a valid `.txt` file path as input.

**Implementation:**
- Open and read file with UTF-8 encoding
- Pass full text to summarisation prompt
- Write output file; verify it is non-empty
- Print confirmation: `✅ Summary written to summary_[filename].txt`
- If output is empty or file write fails, raise a descriptive error

---

## Skill 5: CRAFT Self-Check Report

**What it does:**
After generating the summary, prints a structured checklist showing which completeness checks passed or failed.

**Output format:**
```
=== CRAFT Completeness Check ===
[PASS] All numbered clauses present
[PASS] No modal verbs weakened
[PASS] All penalty/exception clauses flagged [CRITICAL]
[PASS] Output file written: summary_policy_hr_leave.txt
================================
```

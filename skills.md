# skills.md — UC-0B: Summary That Changes Meaning

## Skill: ClauseExtraction

**Purpose:** Extract every discrete rule, condition, exception, and penalty from a structured policy document without merging or omitting any clause.

**Trigger:** Input is a `.txt` policy document with numbered or lettered clauses.

**Steps:**
1. Split the document on numbered/lettered clause markers (e.g., `1.`, `2.`, `a.`, `b.`)
2. For each clause, identify:
   - The core obligation or entitlement
   - Any conditional triggers (`if`, `unless`, `provided that`, `subject to`)
   - Any exceptions or carve-outs (`except`, `however`, `notwithstanding`)
   - Any penalties or consequences (`will result in`, `shall be deducted`, `may be terminated`)
3. Tag each clause: `[RULE]`, `[CONDITION]`, `[EXCEPTION]`, `[PENALTY]`
4. Preserve all numeric values exactly as written

**Failure modes to avoid:**
- Do NOT skip a clause because it seems redundant — every clause is intentional
- Do NOT round or paraphrase numeric thresholds
- Do NOT treat a conditional rule as unconditional

---

## Skill: FaithfulSummarisation

**Purpose:** Produce a summary that changes nothing about the legal or operational meaning of the source document.

**Trigger:** Called after `ClauseExtraction` produces the tagged clause list.

**Steps:**
1. For each tagged clause, write one concise summary sentence
2. Preserve the tag (`[EXCEPTION]`, `[PENALTY]`) in the output
3. Group sentences under the same section headings as the source
4. Do a completeness check: count clauses in source vs. clauses in summary — they must match
5. Do a numeric check: every number in the source must appear in the summary

**Failure modes to avoid:**
- Do NOT summarise two clauses as one
- Do NOT drop the exception just because the main rule is present
- Do NOT change `must` to `should` or `may`

---

## Skill: OutputWriter

**Purpose:** Write the completed summary to `summary_hr_leave.txt` in a clean, readable format.

**Trigger:** Called after `FaithfulSummarisation` completes.

**Steps:**
1. Write a header: `POLICY SUMMARY — [Document Name] — Generated: [date]`
2. Write section headings matching the original
3. Under each heading, write the summary bullets with tags preserved
4. Write a footer: `CLAUSE COUNT: [n] | COMPLETENESS CHECK: PASSED`
5. Save to `summary_hr_leave.txt`

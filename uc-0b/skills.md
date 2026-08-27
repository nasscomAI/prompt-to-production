# skills.md — UC-0B Skill Contracts

## Purpose
Define the minimum skill interfaces needed to produce a legally faithful, clause-complete summary for UC-0B.

## Skill: `retrieve_policy`

### Description
Loads a `.txt` policy document and returns structured numbered clauses for downstream summarization and verification.

### Input
- `input_path` (string): path to policy text file (expected: `../data/policy-documents/policy_hr_leave.txt`)

### Output
- `clauses` (array of objects), one object per numbered clause:
  - `clause_id` (string) — example: `"2.3"`
  - `raw_text` (string) — exact clause text from source
  - `obligation` (string) — normalized obligation statement from clause
  - `binding_verbs` (array[string]) — legal force tokens present (for example: `must`, `requires`, `will`, `not permitted`, `forfeited`)
  - `conditions` (array[string]) — all explicit qualifiers/conditions in clause

### Acceptance Criteria
- Parses and returns all targeted numbered clauses from source.
- Preserves clause text exactly in `raw_text`.
- Does not invent clauses or infer unstated conditions.

---

## Skill: `summarize_policy`

### Description
Takes structured policy clauses and produces a compliant summary file with one line per clause while preserving legal meaning.

### Input
- `clauses` (array): structured clause list produced by `retrieve_policy`
- `output_path` (string): destination summary file (expected: `summary_hr_leave.txt`)

### Output
- Summary lines written to output file, format:
  - one line per clause
  - clause id prefix required (example: `2.3: ...`)
  - if paraphrase risks meaning loss, emit verbatim line as:
    - `FLAG_VERBATIM: <exact clause text>`

### Compliance Rules (Must Enforce)
1. Include every required numbered clause in output.
2. Preserve all conditions for multi-condition clauses.
3. Preserve binding force (no softening of `must`, `requires`, `will`, `not permitted`, `forfeited`).
4. Add no information not present in source text.

### High-Risk Clause Constraint
- Clause `5.2` must explicitly include both approvers:
  - Department Head
  - HR Director
- Any summary line that omits either approver is invalid.

### Verification Expectations
- Perform coverage check for required clause IDs.
- Detect and reject: `MISSING_CLAUSE`, `CONDITION_DROP`, `OBLIGATION_SOFTENING`, `SCOPE_BLEED`.
- Regenerate only failed lines and re-run full verification before final write.

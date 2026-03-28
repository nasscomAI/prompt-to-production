# UC-0B Skills

## Skill: retrieve_policy

### Purpose
Load the source policy file and return structured numbered clauses for downstream summarization.

### Input
- file_path: string (expected: ../data/policy-documents/policy_hr_leave.txt)

### Output
- clauses: ordered list
  - clause_id: string (example: 2.3)
  - clause_text: string (exact source text)
  - binding_verb: string (must, requires, will, not permitted, etc.)
- inventory_check:
  - clause_count: integer
  - numbered_clause_ids: list of strings

### Behavior Rules
1. Preserve clause order and original wording.
2. Extract numbered clauses only; do not paraphrase.
3. Keep full clause text to support condition-level validation.

### Error Handling
- MISSING_INPUT_FILE: input path does not exist or cannot be read.
- INVALID_CLAUSE_STRUCTURE: numbering is malformed or cannot be parsed reliably.

## Skill: summarize_policy

### Purpose
Generate a meaning-preserving summary with clause references and strict condition fidelity.

### Input
- clauses: ordered list from retrieve_policy

### Output
- summary_lines: ordered list
  - clause_id: string
  - summary_text: string
  - flags: optional list (VERBATIM_REQUIRED)
- validation_report:
  - missing_clauses: list
  - condition_drops: list
  - obligation_softening: list
  - scope_bleed_phrases: list

### Behavior Rules
1. Emit one summary line per numbered clause.
2. Preserve all clause conditions; do not collapse multi-approver requirements (5.2 must keep both approvers).
3. Preserve obligation strength (must/requires/will/not permitted).
4. Use only source information; remove scope-bleed language.
5. If safe compression is not possible, quote clause verbatim and set VERBATIM_REQUIRED.

### Error Handling
- MISSING_CLAUSE: any source clause missing in summary output.
- CONDITION_DROP: any sub-condition omitted in summary.
- OBLIGATION_SOFTENING: binding verb strength reduced.
- SCOPE_BLEED: non-source generalized policy language detected.

## RICE Priorities

Scoring model: R (clause coverage from 1-10), I (1-3), C (0-1), E (1-3). Score = (R x I x C) / E.

| Priority | Workflow Improvement | R | I | C | E | Score | Implementation Focus |
|---|---|---:|---:|---:|---:|---:|---|
| P1 | Completeness validator in summarize_policy | 10 | 3 | 0.95 | 1 | 28.50 | Fail output if any numbered clause is missing. |
| P2 | Condition-integrity validator (incl. clause 5.2 dual approval) | 10 | 3 | 0.90 | 1 | 27.00 | Block summaries that omit required sub-conditions. |
| P3 | Obligation-strength parity check | 10 | 3 | 0.85 | 1 | 25.50 | Prevent must/requires/not permitted from being softened. |
| P4 | Scope-bleed detector | 10 | 2 | 0.85 | 1 | 17.00 | Reject non-source assumptions or generic policy phrases. |
| P5 | Verbatim fallback path | 4 | 2 | 0.80 | 1 | 6.40 | Use quote + VERBATIM_REQUIRED when summarization is lossy. |

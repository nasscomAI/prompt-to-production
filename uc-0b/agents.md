# UC-0B Agents

## Agent: policy_summary_guardian

### Role
Produce a meaning-preserving summary of policy_hr_leave.txt with clause-level fidelity. The agent must prioritize legal/operational accuracy over brevity.

### Objective
Generate uc-0b/summary_hr_leave.txt where every numbered source clause is represented without dropped conditions, softened obligations, or added assumptions.

### Allowed Context
- Use only the input policy text.
- Use clause numbers and exact wording from the source.
- Do not use external HR practices, generic policy knowledge, or inferred norms.

### Output Contract
- Summary lines are tagged with clause references (example: 2.3, 5.2).
- Every numbered clause from source appears exactly once in the summary output.
- If summarization risks meaning loss, include verbatim clause text and append [FLAG: VERBATIM_REQUIRED].

### Required Workflow
1. Build a clause inventory from the source text.
2. Draft one summary statement per clause.
3. Validate each statement for condition completeness and binding verb strength.
4. Reject or rewrite any line with scope bleed or inferred guidance.
5. Run final completeness check before writing output.

### Hard Enforcement Rules
1. Include all numbered clauses; no omissions.
2. Preserve all conditions in multi-condition clauses. For 5.2, both Department Head and HR Director approvals are mandatory.
3. Preserve obligation strength (must/requires/not permitted/will). Never weaken to soft language.
4. Never add non-source phrasing such as standard practice or generally expected.
5. If a clause cannot be compressed safely, quote verbatim and flag it.

## RICE Priorities

Scoring model: R (clause coverage from 1-10), I (1-3), C (0-1), E (1-3). Score = (R x I x C) / E.

| Priority | Capability | R | I | C | E | Score | Agent Behavior Requirement |
|---|---|---:|---:|---:|---:|---:|---|
| P1 | Clause completeness gate | 10 | 3 | 0.95 | 1 | 28.50 | Block output if any numbered clause is missing. |
| P2 | Multi-condition integrity check | 10 | 3 | 0.90 | 1 | 27.00 | Reject summaries that drop sub-conditions (especially 5.2). |
| P3 | Obligation-strength preservation | 10 | 3 | 0.85 | 1 | 25.50 | Keep binding force equivalent to source verbs. |
| P4 | Scope-bleed suppression | 10 | 2 | 0.85 | 1 | 17.00 | Remove all external/generalized policy language. |
| P5 | Verbatim fallback for lossy clauses | 4 | 2 | 0.80 | 1 | 6.40 | Emit source quote with VERBATIM_REQUIRED flag when needed. |

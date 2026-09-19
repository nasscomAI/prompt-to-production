# agents.md — UC-0B Summary That Changes Meaning

role: >
  HR policy summariser for the City Municipal Corporation. It shortens the wording
  of one policy document at a time without changing what any clause obliges,
  permits or forbids. It does not interpret, advise, compare with other policies,
  or explain "why" a rule exists.

intent: >
  A summary file in which every numbered clause of the source appears on its own
  line, prefixed with its clause number (e.g. "[5.2]"), in source order. For each
  clause the summary keeps every number, every binding verb (must / will / requires /
  may / cannot / not permitted), every strength qualifier (only, regardless,
  under any circumstances) and every named approver. A reviewer can verify it by
  checking the 10 inventory clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2)
  against the source line by line.

context: >
  Allowed: the text of the single policy file passed with --input. Not allowed:
  other policy documents, general HR knowledge, "common practice" in government
  organisations, or any assumption about how the policy is applied in reality.

enforcement:
  - "Every numbered clause in the source must be present in the summary with its clause number — a clause count mismatch is a failure, not a style choice."
  - "Multi-condition obligations must keep ALL conditions. Clause 5.2 must name both the Department Head AND the HR Director, and keep 'Manager approval alone is not sufficient'. Dropping one approver is a condition drop, even if 'requires approval' survives."
  - "Binding verbs and strength qualifiers are never softened: 'must' stays 'must', 'not permitted under any circumstances' stays exactly that, 'regardless of subsequent approval' is never removed. 'Must' is never rewritten as 'should' or 'is expected to'."
  - "Never add information that is not in the source. Phrases such as 'as is standard practice', 'typically', 'generally', 'employees are expected to' are banned unless they appear in the source text."
  - "Refusal condition: if a clause cannot be shortened without losing a number, a binding verb, a qualifier or a named role, quote it verbatim and mark it [VERBATIM]. If the file has no numbered clauses, refuse to summarise rather than paraphrase free text."
  - "The run fails (non-zero exit) if any of the 10 inventory clauses is missing or has lost a required fact, or if a banned scope-bleed phrase appears — a failed summary must not be used."

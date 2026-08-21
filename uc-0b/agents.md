# agents.md — UC-0B Policy Summariser
# DRAFT 2 — after CRAFT cycle 1. Failure observed: clause omission.

role: >
  A summariser for City Municipal Corporation policy documents.

intent: >
  A clause register in which every numbered clause in the source appears exactly
  once under its own clause ID. Verifiable: the output clause-ID set must equal
  the source clause-ID set.

context: >
  The policy document passed to --input.

enforcement:
  - "COMPLETENESS: Every numbered clause N.M present in the source must appear in the summary under its own clause ID. The run fails and exits non-zero if the output clause-ID set is not identical to the source clause-ID set. Ten clauses are additionally asserted by ID as a hard gate: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2."
  - "The summary should be accurate and should not misrepresent the policy."
  - "The summary should be concise."
  - "If something is unclear, say so."

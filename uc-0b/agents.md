# agents.md — UC-0B Policy Summariser
# DRAFT 3 — after CRAFT cycle 2. Failure observed: condition dropping in clause 5.2.

role: >
  A summariser for City Municipal Corporation policy documents.

intent: >
  A clause register in which every numbered clause in the source appears exactly
  once under its own clause ID, with its binding verb named and all of its
  conditions enumerated separately. Verifiable: (a) the output clause-ID set
  equals the source clause-ID set, and (b) for each clause, every critical token
  from the source clause still appears in that clause's output block.

context: >
  Permitted input: the text of the single policy file passed to --input, and
  nothing else. Explicitly excluded: the other policy documents in
  data/policy-documents/, and any inference about what the policy probably
  intends where it is silent.

enforcement:
  - "COMPLETENESS: Every numbered clause N.M present in the source must appear in the summary under its own clause ID. The run fails and exits non-zero if the output clause-ID set is not identical to the source clause-ID set. Ten clauses are additionally asserted by ID as a hard gate: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2."
  - "CONDITION PRESERVATION: A multi-condition obligation must retain all of its conditions, each rendered as a separate enumerated line. Where a clause names more than one approver, all approvers must be listed and the block must be marked MULTI-APPROVER — ALL REQUIRED. Clause 5.2 must carry both 'Department Head' and 'HR Director'; retaining only one is a condition drop and fails the run, even though the sentence still reads as an approval requirement."
  - "TOKEN SURVIVAL: For each clause, every number, form code (Form HR-L1), named role or body, binding verb (must / must not / will / requires / may / cannot / not permitted / is entitled / are forfeited) and absolute qualifier (only, regardless, unless, not valid, not sufficient, under any circumstances) present in the source clause must be present in that clause's output block. Any token that does not survive triggers the verbatim fallback for that clause."
  - "REFUSAL / VERBATIM FALLBACK: If a clause cannot be rendered without losing a critical token, the summariser must not paraphrase it. It must emit the source text verbatim, mark the block [FLAG: VERBATIM-REQUIRED — condensing this clause would drop a binding condition], and count it in the flag total. Refusing to compress is always preferred to compressing lossily."

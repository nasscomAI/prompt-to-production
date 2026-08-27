# agents.md
# UC-0B: Policy Summarizer - Clause Preservation & Condition Detection

role: >
  Policy Summarizer Agent creates concise policy summaries that preserve
  all numbered clauses and binding conditions without omission, softening,
  or scope bleed. It operates strictly within source document boundaries.

intent: >
  All 10 indexed clauses present with core obligations intact.
  Multi-condition obligations preserve ALL conditions.
  Binding verbs match source exactly. No scope bleed.
  Verifiable 100% clause coverage.

context: >
  Retrieves policy_hr_leave.txt sections 2-7.
  References only document information.
  Cannot use external government practices knowledge.

enforcement:
  - " Clauses 2.3 2.4 2.5 2.6 2.7 3.2 3.4 5.2 5.3 7.2 must appear\
 - \Clause 5.2: Department Head AND HR Director not just approval required\
 - \Verbs match source: must will requires not permitted - no softening\
 - \Reject: as is standard practice typically generally expected\
 - \Refuse if document ambiguous on any clause\

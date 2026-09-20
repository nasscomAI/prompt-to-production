# agents.md — UC-0B Policy Summarizer

role: >
  Compliance-focused policy summarization engineer. Extracts and condenses
  only the text of policy_hr_leave.txt into a faithful summary. No external
  knowledge, no standard-practice filler, no invented rules.

intent: >
  Produce uc-0b/summary_hr_leave.txt that covers all 10 critical clauses
  (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) with one item per clause,
  each labeled with its clause number. Verifiable by: every required number
  appears, every numeric limit/deadline matches source, AND/OR approvers are
  intact, and no sentence contains rules absent from source.

context: >
  Allowed input: data/policy-documents/policy_hr_leave.txt text only, parsed
  as numbered clauses. Exclusions: do NOT use outside HR knowledge, standard
  practice, other policies, or assumptions about typical government rules.
  Do NOT summarize other files. Do NOT add obligations, exceptions, or
  softening adverbs not in source.

enforcement:
  - "1. Every required numbered clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must appear in the final summary with its clause number as a heading; test fails if any number is missing."
  - "2. Never remove a condition: 2.4 keeps written + before-commencement + verbal-invalid; 5.2 keeps Department Head AND HR Director + manager-alone-insufficient; test fails if any condition is dropped."
  - "3. Preserve AND/OR relationships exactly: 5.2 uses AND (both approvers required), 3.4 uses OR (before OR after holiday); test fails if AND is rewritten as OR or vice versa."
  - "4. Preserve numeric limits and deadlines verbatim: 14 days, 5 days, 31 December, Jan-Mar, 3+ days, 48 hours, 30 days; test fails on any altered number or dropped deadline."
  - "5. Never add rules not in source: ban filler like typically, generally, standard practice, usually; test fails if any summary sentence states a rule with no source span."
  - "6. If a clause cannot be summarized safely, quote it verbatim in quotes and append [QUOTED VERBATIM]; test fails on paraphrase that changes must/will/requires/not-permitted strength."
  - "7. Include the clause number with every summary item (e.g. [2.3]); test fails on any item without its number."

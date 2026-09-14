# agents.md — UC-0B Summary That Changes Meaning

role: >
  Policy Summarizer agent for policy_hr_leave.txt. Produces a clause-by-clause
  summary of the 10 required clauses (2.3–2.7, 3.2, 3.4, 5.2, 5.3, 7.2). Does
  not paraphrase freely — it condenses wording while preserving every binding
  condition. Runs offline via app.py, stdlib only.

intent: >
  A correct run writes summary_hr_leave.txt containing one entry per required
  clause, in clause-number order, each entry starting with the clause number
  in brackets. Correctness is checked by: (1) all 10 clauses present — none
  silently dropped; (2) multi-condition clauses (2.6, 5.2) keep every
  condition, not just the first; (3) no sentence appears that isn't traceable
  to the source text — no "as is standard practice", "typically", "generally
  expected" additions.

context: >
  Allowed: only the text of policy_hr_leave.txt. Excluded: any general
  knowledge about HR policy, any other policy document, any assumption about
  "typical" municipal practice not stated in this file.

enforcement:
  - "Every one of the 10 required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4,
     5.2, 5.3, 7.2) must appear in the output. If a clause is missing from the
     source text, the output states that explicitly instead of omitting the
     line."
  - "Multi-condition obligations must preserve every condition. Clause 5.2 in
     particular requires BOTH Department Head AND HR Director approval —
     summarizing it as 'requires approval' alone is a failure."
  - "Never add information, examples, or framing not present in the source
     document. Banned phrases: 'as is standard practice', 'typically',
     'generally expected', 'in most organisations' — none of these appear in
     the source, so none may appear in the summary."
  - "Obligation strength must not soften: 'must' / 'will' / 'requires' /
     'not permitted' in the source must not become 'should' / 'may' /
     'is recommended' in the summary."
  - "Refusal condition: if a clause cannot be condensed without losing a
     condition, quote the clause verbatim instead of summarizing it, and mark
     it '[verbatim]'."

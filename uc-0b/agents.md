# agents.md - UC-0B Policy Summarizer

role: >
  Summarize the supplied policy text for a reader while preserving every
  obligation, condition, actor, deadline, threshold, and consequence.

intent: >
  Produce a concise, source-grounded summary that explicitly covers clauses
  2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2, with each clause
  reference and its binding meaning intact.

context: >
  Use only the supplied policy_hr_leave.txt document. Do not import standard
  practice, organizational assumptions, or facts from other policy documents.

enforcement:
  - "every numbered clause in the source must appear in the summary with its clause reference"
  - "preserve every condition in multi-condition obligations; clause 5.2 must name both Department Head and HR Director approval"
  - "preserve binding verbs, deadlines, thresholds, exceptions, and consequences; do not soften must, will, requires, or not permitted"
  - "never add information that is not present in the source document"
  - "if a clause cannot be summarized without meaning loss, quote it verbatim and flag it for review rather than guessing"

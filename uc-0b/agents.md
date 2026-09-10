# agents.md — UC-0B Summary That Changes Meaning

role: >
  HR leave-policy summariser. Produces a faithful condensed restatement of
  policy_hr_leave.txt only. Operates strictly within the source document;
  must not import outside HR knowledge, standard practice, or assumptions.

intent: >
  A correct output (summary_hr_leave.txt) lists every numbered clause of
  the source, preserves each binding verb and every condition, and cites
  the clause number for each bullet. Verifiable by: `python app.py --input
  ../data/policy-documents/policy_hr_leave.txt --output
  summary_hr_leave.txt` running without crash, all 10 critical clauses
  (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) present with exact
  limits, dates, approvers, and prohibitions intact.

context: >
  Allowed information: the text of policy_hr_leave.txt (HR-POL-001,
  v2.3, effective 1 April 2024) only. Exclusions: no other policy files,
  no web knowledge, no phrases such as "as is standard practice",
  "typically", "generally expected", "in government organisations".
  Every factual sentence must trace to a numbered clause.

enforcement:
  - "Every numbered clause in the source must appear in the summary with its clause number cited (e.g. [2.3]). No clause may be omitted, including 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2."
  - "Multi-condition obligations must preserve ALL conditions: 5.2 requires approval from BOTH the Department Head AND the HR Director (manager approval alone is not sufficient); 2.6 keeps both the 5-day limit and the 31 December forfeiture; 3.2 keeps the 3-day threshold, the medical-certificate requirement, and the 48-hour deadline together."
  - "Never add information not present in the source document. No softening of obligations (must/requires/will/not permitted stay binding) and no scope bleed."
  - "If a clause cannot be summarised without meaning loss, quote it verbatim and append [QUOTED VERBATIM — REVIEW]. Never guess or paraphrase away a binding condition."

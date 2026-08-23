# agents.md — UC-0B HR Leave Policy Summariser

role: >
  A municipal policy summarisation agent for the City Municipal Corporation
  HR department. It receives one plain-text policy document and produces a
  structured summary that preserves every numbered clause, every binding
  obligation, and every multi-condition requirement exactly as written.
  Its operational boundary is strict document-in / summary-out: it
  restructures and reports; it never paraphrases meaning, never interprets,
  and never supplements the source with outside knowledge. It runs fully
  offline and deterministically — identical input always yields a
  byte-identical output file.

intent: >
  Running `python app.py --input ../data/policy-documents/policy_hr_leave.txt
  --output summary_hr_leave.txt` produces summary_hr_leave.txt in which:
  (1) every numbered clause of the source (1.1 through 8.2 — 29 clauses)
  appears under its correct section heading with its clause number intact;
  (2) all ten critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3,
  7.2) preserve their complete obligations, including clause 5.2's requirement
  of approval from BOTH the Department Head AND the HR Director;
  (3) no sentence adds information absent from the source document;
  (4) mandatory language ("must", "requires", "not permitted under any
  circumstances") keeps its force — never weakened to "should", "may" or "can";
  (5) the run ends with a printed completeness ledger proving coverage.
  Verifiable pass condition: the ledger reports every clause present and
  10/10 critical clauses verified.

context: >
  Allowed: the exact text of the .txt policy document supplied via --input —
  its header lines, section headings, clause numbers, and clause wording.
  Excluded explicitly: external knowledge of employment law or government
  practice; boilerplate phrases not in the source such as "as is standard
  practice", "typically in government organisations", or "employees are
  generally expected to"; invented clauses, approvers, deadlines, or
  quantities; any document other than the one named in the run command.
  No network access. No random or time-based behaviour.

enforcement:
  - "Completeness: every numbered clause found in the source must appear in the summary under its correct section heading with its clause number preserved. The tool counts clauses extracted versus clauses rendered and must report full coverage."
  - "Multi-condition preservation: where one obligation carries multiple conditions or multiple approvers — e.g. clause 5.2 LWP requires approval from the Department Head AND the HR Director — ALL conditions must survive into the summary together. Silently dropping or merging one condition is a failure, even if the remaining text is accurate."
  - "No addition: the summary may contain only information present in the source document. Scope bleed — phrases like 'as is standard practice', 'typically in government organisations', 'employees are generally expected to' — is forbidden."
  - "No softening: binding verbs keep their force. 'must' stays 'must'; 'requires' stays 'requires'; 'not permitted under any circumstances' stays absolute; quantities and deadlines (14 days advance notice, max 5 carry-forward days, Jan-Mar usage window, 48 hours, 30 days, Form HR-L1) appear unchanged."
  - "Verbatim fallback: any clause carrying a compound obligation, multiple conditions, an absolute prohibition, or a threshold paired with a consequence is quoted verbatim from the source and tagged [VERBATIM] instead of compressed, so no meaning can be lost in summarisation."
  - "Refusal: if the input file is missing, unreadable, or parses to zero sections or zero clauses, exit non-zero and write no output. If any of the ten critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) cannot be found in the parsed input, exit non-zero rather than emit a summary that silently omits them."

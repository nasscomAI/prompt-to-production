# skills.md

skills:
  - name: retrieve_policy
    description: Loads the HR leave policy .txt file and parses it into structured, numbered clause sections.
    input: Path to a policy .txt file (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: >
      An ordered list of {clause_number, clause_text} objects, one per numbered
      clause found in the document (e.g. "2.3", "2.4" ... "8.2"), with wrapped
      lines joined into a single clause_text string.
    error_handling: >
      If the file is missing or contains no recognizable numbered clauses,
      raise a clear error naming the file path rather than returning an empty
      or fabricated summary.

  - name: summarize_policy
    description: Takes the structured clause sections from retrieve_policy and produces a complete, per-clause compliant summary.
    input: The ordered list of {clause_number, clause_text} objects from retrieve_policy.
    output: >
      A text summary with one line per clause, in document order, each
      formatted as "<clause_number>: <preserved obligation text>" — multi-
      condition clauses are quoted verbatim and marked [VERBATIM].
    error_handling: >
      If a clause's obligation cannot be shortened without dropping a
      condition, approver, or threshold, output it verbatim marked
      [VERBATIM] instead of a paraphrase. Never omits a clause to keep the
      summary shorter.

# skills.md — UC-0B Policy Summary

skills:
  - name: retrieve_policy
    description: Load the policy .txt file and split it into structured numbered clauses keyed by clause number.
    input: >
      input_path (str) to a UTF-8 text policy document whose clauses are numbered
      like 2.3, 5.2 (section.clause).
    output: >
      An ordered mapping of clause_number (str) -> clause_text (str), preserving
      the source wording of each clause exactly. Also exposes the raw document
      text for verbatim quoting.
    error_handling: >
      If the file is missing or unreadable, raise a clear error before any
      summarisation is attempted. If the expected clause-numbering pattern is not
      found, return whatever clauses were parsed plus a list of expected clause
      numbers that were not located, so the caller can refuse rather than guess.

  - name: summarize_policy
    description: Turn the structured clauses into a compliant, condition-complete digest with clause references and a self-check.
    input: >
      The clause mapping from retrieve_policy, plus the fixed required set of 10
      binding clause numbers: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2.
    output: >
      A summary string where each of the 10 binding clauses appears, prefixed by
      its clause number, condition-complete. Any clause that cannot be safely
      condensed is quoted verbatim and tagged [VERBATIM]. The summary content is
      kept pure policy text; the verification report (each required clause number
      as PRESENT/MISSING, and condition checks such as 5.2 both approvers as
      PASS/FAIL) is returned separately for stdout, not blended into the summary
      body.
    error_handling: >
      Never invents text not in the source and never softens a binding verb. If a
      required clause number is absent from the input mapping, it does not
      fabricate the clause: it marks that clause MISSING in the verification
      report and the caller refuses to write a summary claiming completeness.
      Multi-condition clauses that would lose a condition when shortened are
      emitted verbatim instead.

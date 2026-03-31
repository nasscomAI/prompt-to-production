# skills.md
skills:
  - name: retrieve_policy
    description: Loads a .txt policy document and returns structured numbered sections for downstream compliance checks.
    input: File path to a UTF-8 plain text policy document (for example, ../data/policy-documents/policy_hr_leave.txt).
    output: JSON object with ordered section entries: clause_id, heading (optional), raw_text, and source_line_span.
    error_handling: Returns a blocking error if the file cannot be read, is not plain text, or required clauses cannot be detected.

  - name: summarize_policy
    description: Produces a compliant policy summary from structured sections while preserving obligations and clause-level meaning.
    input: Structured sections from retrieve_policy plus required clause checklist [2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2].
    output: Summary text with explicit clause references, preserved binding verbs, and a verification block confirming checklist coverage.
    error_handling: If any clause is missing, ambiguous, or cannot be summarized without meaning loss, quote the original clause verbatim and flag unresolved items instead of inferring.

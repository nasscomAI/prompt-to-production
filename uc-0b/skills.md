skills:
  - name: retrieve_policy
    description: Loads a plain-text policy document and parses it into structured numbered sections and individual numbered clauses.
    input: Filepath string pointing to the policy document (e.g., policy_hr_leave.txt).
    output: Structured dictionary or list mapping section titles and clause numbers (e.g., 1.1, 2.3) to their raw clause text.
    error_handling: Raises FileNotFoundError if input path is invalid; strips non-text formatting anomalies and validates that numbered clauses are properly extracted.

  - name: summarize_policy
    description: Processes structured policy clauses to generate a concise summary that retains all numbered clauses, exact binding verbs, and multi-condition approvals without scope bleed.
    input: Structured data mapping section headers and clause identifiers to text.
    output: String representing the formatted policy summary document preserving all clause numbers and binding obligations.
    error_handling: Verifies that every input clause is present in the final summary; raises an error or preserves verbatim clause text if compression risks condition dropping.

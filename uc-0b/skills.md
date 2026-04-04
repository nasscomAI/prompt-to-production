#skills:
  - name: retrieve_policy
    description: Loads the HR leave policy file and structures it into numbered clauses for strict processing.
    input: string (file path to policy_hr_leave.txt)
    output: object (dictionary mapping clause numbers to full clause text)
    error_handling: >
      If file is missing, unreadable, or empty, return error "POLICY_LOAD_FAILURE" and stop execution.

  - name: summarize_policy
    description: Produces a clause-referenced summary of HR leave policy while preserving all obligations and conditions exactly.
    input: object (structured clauses from retrieve_policy)
    output: string (strict summary with clause references, no meaning change)
    error_handling: >
      If any clause is missing, incomplete, or loses conditions during summarization, return error "SUMMARY_INTEGRITY_FAILURE" and do not generate output.
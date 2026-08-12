skills:
  - name: retrieve_policy
    description: Reads the HR policy document and extracts numbered clauses.
    input: Path to policy_hr_leave.txt
    output: Structured numbered policy sections
    error_handling: Return an error if the file is missing or unreadable.

  - name: summarize_policy
    description: Produces an accurate policy summary while preserving every mandatory condition.
    input: Structured policy sections
    output: Clause-by-clause compliant summary
    error_handling: Quote the original clause if summarization risks changing meaning.
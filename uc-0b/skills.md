skills:
  - name: retrieve_policy
    description: Load a policy text file and identify its numbered clauses.
    input: Policy text file path.
    output: Ordered list of numbered policy clauses.
    error_handling: Report a missing or unreadable source file clearly.

  - name: summarize_policy
    description: Produce a clause-referenced summary while preserving all obligations and conditions.
    input: Ordered list of numbered policy clauses.
    output: Clause-referenced policy summary text.
    error_handling: Preserve the source wording when summarization could lose meaning.

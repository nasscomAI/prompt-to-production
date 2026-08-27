skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and converts it into structured numbered clauses.
    input: >
      File path to a .txt policy document containing numbered policy clauses.
    output: >
      Structured list of policy clauses in the format:
      [
        { "clause_number": "2.3", "text": "policy clause text" },
        { "clause_number": "2.4", "text": "policy clause text" }
      ]
    error_handling: >
      If the file cannot be found or parsed, return an error indicating
      invalid file path or unreadable policy document.

  - name: summarize_policy
    description: Generates a compliant summary of the HR leave policy while preserving all obligations and conditions.
    input: >
      Structured policy clauses produced by retrieve_policy.
    output: >
      A summarized policy document that includes each clause reference and
      preserves all obligations, conditions, and binding verbs.
    error_handling: >
      If a clause cannot be summarized without meaning loss, quote the
      clause verbatim and flag it for review.

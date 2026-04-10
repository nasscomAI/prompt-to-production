skills:
  - name: retrieve_policy
    description: Loads and reads the HR policy document.
    input:
      type: string
      format: File path to policy document
    output:
      type: string
      format: Raw text content of the document
    error_handling: >
      If file not found → raise error and stop execution.

  - name: summarize_policy
    description: Generates a summary that preserves all clauses and conditions.
    input:
      type: string
      format: Policy document text
    output:
      type: string
      format: Faithful summary preserving all obligations
    error_handling: >
      If summarization removes clauses → reject output.
      If conditions are altered → regenerate summary.
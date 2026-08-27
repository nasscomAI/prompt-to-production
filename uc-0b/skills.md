skills:
  - name: retrieve_policy
    description: Loads .txt policy file and returns content as structured numbered sections.
    input: File path (string) to the .txt policy document.
    output: Structured numbered sections containing the text of the policy clauses.
    error_handling: Returns structured error if the file is not found or cannot be read.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured numbered sections of the policy.
    output: A generated compliant summary indicating every numbered clause and multi-condition obligations.
    error_handling: Quotes clause verbatim and flags it if it cannot be summarised without meaning loss.

skills:
  - name: retrieve_policy
    description: Loads a text policy file and extracts its numbered clauses for structured processing.
    input: Path to a .txt policy document.
    output: A structured mapping of clause numbers to clause text.
    error_handling: If the file cannot be read, return an error message and stop processing.

  - name: summarize_policy
    description: Produces a compliant clause-preserving summary from structured policy sections.
    input: Structured clause mapping from the policy document.
    output: A summary text containing clause references and obligation-preserving summaries.
    error_handling: If a clause is missing, ambiguous, or cannot be safely compressed, include the original clause text and mark it with FLAG: VERBATIM.
skills:
  - name: retrieve_policy
    description: Loads .txt policy file and returns its content as structured numbered sections.
    input: File path to the .txt policy document.
    output: Structured numbered sections extracted from the policy text.
    error_handling: Returns an error if the file cannot be found or if formatting is unreadable.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured numbered sections of the policy document.
    output: A comprehensive summary preserving all clauses and conditions.
    error_handling: Flags verbatim clauses if they cannot be summarized without meaning loss.

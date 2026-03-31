skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to the .txt policy document (string).
    output: Structured numbered sections containing clauses, core obligations, and binding verbs (JSON or structured string).
    error_handling: Returns an error if the file cannot be read or lacks valid numbered clauses.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with exact clause references.
    input: Structured numbered sections of the policy (JSON or structured string).
    output: A summarized text document with references to all original clause numbers.
    error_handling: Refuses to guess; if a clause cannot be summarised without meaning loss, quotes it verbatim and flags it.

# skills.md

skills:
  - name: retrieve_policy
    description: Loads a local .txt policy file and parses it into structured numbered sections.
    input: Filepath to the policy text document (string).
    output: A structured representation of the policy clauses (dictionary or list of clauses).
    error_handling: Raises an error if the file cannot be found or read, or if the format doesn't contain numbered clauses.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that perfectly preserves all obligations and conditions with clause references.
    input: Structured policy sections (dictionary or list of clauses).
    output: A summarized text document string with explicit clause references.
    error_handling: Verbatim quotes and flags any clause that it cannot summarize without potentially losing meaning or dropping conditions.

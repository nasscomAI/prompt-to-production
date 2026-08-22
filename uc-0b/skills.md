skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns content as structured numbered sections.
    input: File path (string).
    output: Raw text string of the policy document.
    error_handling: Raise an error if the file cannot be found or read.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: Raw policy text (string).
    output: Summary string.
    error_handling: Deterministically validate that all critical clauses (e.g. 5.2) and conditions are preserved. If meaning loss is detected, append the verbatim clause with a flag.

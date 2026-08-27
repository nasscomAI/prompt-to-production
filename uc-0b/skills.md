skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) referencing a .txt policy document.
    output: Structured numbered sections (list or dictionary) extracted from the policy text.
    error_handling: Return an explicit error if the file cannot be found, read, or if numbered sections cannot be successfully parsed.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant, complete summary with clause references.
    input: Structured numbered sections of a policy.
    output: A compliant summary string with clause references.
    error_handling: Return the original clause verbatim and flag it if it cannot be summarized without modifying meaning.

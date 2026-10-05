# skills.md

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content as structured numbered sections.
    input: File path (string).
    output: A structured text or list of numbered sections representing the policy content.
    error_handling: If the file is missing or unreadable, return a descriptive error and stop processing.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant summary with clause references.
    input: Structured policy text from retrieve_policy.
    output: A plain text summary containing the 10 core clauses accurately summarized.
    error_handling: If an obligation cannot be summarized without losing conditions (like multiple approvers), quote the clause verbatim and flag it.

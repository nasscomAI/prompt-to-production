skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to the .txt policy document (string format).
    output: Structured text representing the policy, separated into clear numbered sections.
    error_handling: Return an explicit error message if the file is missing or unreadable.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured text containing numbered clauses.
    output: A text summary containing explicit clause references, maintaining all obligation conditions.
    error_handling: If a clause cannot be summarized without loss of meaning, it must be quoted verbatim and flagged.

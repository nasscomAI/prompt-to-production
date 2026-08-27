
skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured, numbered sections.
    input: File path string pointing to the text document.
    output: String of structured sections exactly as they appear in the source document.
    error_handling: Raise an error if the file cannot be found or read.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references based strictly on the agent's rules.
    input: String of structured text sections from retrieve_policy.
    output: Formatted text summary containing all numbered clauses and multi-condition obligations.
    error_handling: If a clause cannot be summarized without meaning loss, quote it verbatim and flag it.

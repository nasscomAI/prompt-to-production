skills:
  - name: retrieve_policy
    description: Loads .txt policy file and returns content as structured numbered sections.
    input: File path to a .txt policy document (String).
    output: Structured numbered sections of the policy document (List of dictionaries or JSON).
    error_handling: If the file is missing or unreadable, return an explicit error and halt. If text lacks numbered sections, return the raw text with a warning flag.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured numbered sections of the policy document (List of dictionaries or JSON).
    output: A compliant summary document with explicit clause references (Text or Markdown).
    error_handling: If a clause is ambiguous or cannot be summarized without meaning loss, quote it verbatim and flag it. If input is empty, return an error.

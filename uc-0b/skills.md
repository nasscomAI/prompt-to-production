# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: File path string to a .txt policy file.
    output: Structured text containing numbered sections and their corresponding content.
    error_handling: Return an error if the file does not exist or cannot be parsed into numbered sections.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references, strictly preserving all conditions.
    input: Structured representation of numbered policy sections.
    output: A text summary where every numbered clause is present and all multi-condition obligations have preserved all their conditions, avoiding scope bleed or obligation softening.
    error_handling: If a clause cannot be safely summarized without meaning loss, quote it verbatim and flag it.

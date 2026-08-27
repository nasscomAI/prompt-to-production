# skills.md

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content mapped as structured numbered sections.
    input: File path to the policy text document.
    output: A dictionary or structured object mapping clause numbers to their exact text content.
    error_handling: Return a critical error if the file cannot be read or sections cannot be safely parsed.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all dependencies and clause references.
    input: Structured sections of the policy text.
    output: A strictly formatted text summary with citations linking every synthesized point to its parent clause.
    error_handling: If a section is ambiguous or summarizing it risks condition dropping, flag it and quote it verbatim instead of returning a confident guess.

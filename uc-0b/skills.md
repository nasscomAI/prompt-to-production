# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Path to the .txt policy file.
    output: Structured content with numbered sections.
    error_handling: Raises an error if the file is not found, unreadable, or improperly formatted.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured content with numbered sections.
    output: Compliant summary with clause references.
    error_handling: Flags and quotes verbatim any clause that cannot be summarized without

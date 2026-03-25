# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: File path (string) to the target .txt policy file.
    output: Structured content string mapped into numbered clauses.
    error_handling: Raise an error if the file is missing, unreadable, or not in .txt format.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary that preserves all conditions and includes clause references.
    input: Structured policy sections (string or object).
    output: A markdown summary containing all 10 mandatory clauses with their specific binding obligations.
    error_handling: Flag a failure if any clause is omitted, any condition is dropped (especially in Clause 5.2), or if unauthorized information is added.

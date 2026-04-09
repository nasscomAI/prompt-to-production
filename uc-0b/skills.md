# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns its content as structured, numbered sections.
    input: File path string to the policy document (e.g., .txt).
    output: Structured representation of the document broken down by numbered clauses.
    error_handling: Raises an error if the file is not found or cannot be parsed into numbered sections.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant, highly accurate summary preserving all conditions (especially multi-party approvals) and clause references.
    input: Structured policy sections (output from retrieve_policy).
    output: A summary string with explicit clause references, quoting and flagging clauses that cannot be safely summarized.
    error_handling: Flags clauses that are too complex to summarize safely without losing meaning.

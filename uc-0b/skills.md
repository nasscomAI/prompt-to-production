skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content organized into structured, numbered sections.
    input:
      type: string
      format: File path to a .txt policy document
    output:
      type: array
      format: Structured objects representing numbered sections
    error_handling: Fails if the file cannot be accessed or parsed into distinct numbered clauses.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with explicit clause references.
    input:
      type: array
      format: Structured numbered sections from retrieve_policy
    output:
      type: string
      format: Text summary preserving all original obligations, verbs, and conditions
    error_handling: Rejects output or explicitly flags clauses verbatim if any numbered clause is omitted, if multi-condition rules are partially dropped, or if scope bleed introduces unstated standard practices.

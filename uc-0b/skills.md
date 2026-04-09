skills:
  - name: retrieve_policy
    description: Loads .txt policy file and returns content as structured numbered sections.
    input: File path to the raw .txt policy file.
    output: Structured representation of the document, broken down into numbered sections and clauses.
    error_handling: Return an error if the file is unreadable, missing, or lacks a discernible numbering format.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured policy sections provided by retrieve_policy.
    output: A cohesive summary document that explicitly references the source clause numbers.
    error_handling: If any multi-condition clause is ambiguous, quote it verbatim and flag it for manual review.

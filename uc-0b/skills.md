skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a .txt policy document.
    output: Structured text segmented by numbered sections and clauses.
    error_handling: If the file cannot be read, return an error. If the file lacks numbered sections, return the full text but flag it as unstructured.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary preserving all clause references and obligations.
    input: Structured text containing numbered policy sections.
    output: A formatted text summary that references each original clause with its core obligation.
    error_handling: If a clause cannot be summarized without risking meaning loss, quote the clause verbatim and flag it for manual review.

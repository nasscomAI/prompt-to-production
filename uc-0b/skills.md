skills:
  - name: retrieve_policy
    description: Loads an HR policy text file and structures it into numbered clauses with section context.
    input: Path to .txt policy document as a string.
    output: List of clause objects, each containing section, clause id, and normalized clause text.
    error_handling: Raises an explicit error if no numbered clauses are found or the file cannot be read.

  - name: summarize_policy
    description: Produces a clause-complete summary from structured policy clauses while preserving obligations.
    input: List of structured clauses from retrieve_policy.
    output: Plain-text summary containing each clause reference and summary/verbatim text.
    error_handling: Fails fast if any source clause is missing in output; uses [VERBATIM] when summarization may lose meaning.

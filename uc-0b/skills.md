skills:
  - name: retrieve_policy
    description: Loads a plain text policy file and converts it into structured numbered sections and clauses.
    input: Path to a .txt policy file.
    output: Ordered structured data containing section headings and numbered clause text.
    error_handling: Reject missing or unreadable files with a clear error and do not fabricate missing clauses.

  - name: summarize_policy
    description: Produces a clause-referenced summary from structured policy sections without dropping conditions.
    input: Structured numbered sections from retrieve_policy.
    output: A text summary containing every clause number and a faithful restatement or verbatim quote.
    error_handling: If a clause cannot be compressed safely, quote it verbatim and mark it as verbatim instead of softening or guessing.

skills:
  - name: retrieve_policy
    description: Loads a `.txt` HR policy file and returns its content as structured numbered sections.
    input: File path string to a policy text file (for example `../data/policy-documents/policy_hr_leave.txt`).
    output: Ordered section objects keyed by clause number (for example `2.3`, `2.4`) with original clause text preserved.
    error_handling: Returns a clear error if file is missing, unreadable, non-text, or if numbered clauses cannot be reliably parsed.

  - name: summarize_policy
    description: Produces a concise, compliance-preserving summary from structured policy sections with clause references.
    input: Structured numbered sections from `retrieve_policy`, including source text for each required clause.
    output: Summary text covering all required clauses with obligations and multi-condition requirements preserved.
    error_handling: Refuses to guess when required clauses are missing or ambiguous; quotes non-preservable clauses verbatim and flags them.

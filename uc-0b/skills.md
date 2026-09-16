skills:
  - name: retrieve_policy
    description: Loads the supplied text policy and extracts its numbered clauses in source order.
    input: A readable UTF-8 .txt policy file path.
    output: Structured numbered sections, each containing a clause reference and its complete source text.
    error_handling: Refuses with a clear error when the file is missing, unreadable, empty, or contains no numbered clauses.

  - name: summarize_policy
    description: Produces a traceable policy summary without omitting clauses, dropping conditions, softening obligations, or adding scope.
    input: Structured numbered sections returned by retrieve_policy.
    output: A clause-referenced summary containing every source clause and preserving all obligations, conditions, exceptions, thresholds, deadlines, approvers, and consequences.
    error_handling: If meaning cannot be preserved, quotes the affected clause verbatim and flags it; refuses to guess when the source or clause structure is ambiguous.

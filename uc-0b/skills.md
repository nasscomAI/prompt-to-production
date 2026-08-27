skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns structured numbered clauses.
    input: |
      Path to a .txt policy document.
    output: |
      Ordered mapping of clause_number → full clause text, plus raw full text.
    error_handling: |
      - If file not found or unreadable: return empty mapping and an error flag.
      - If numbering cannot be parsed: return best-effort sections and flag needs_review.

  - name: summarize_policy
    description: Produces a clause-faithful summary with clause references preserved.
    input: |
      Ordered mapping from retrieve_policy and the expected clause inventory.
    output: |
      List of lines, one per clause, each starting with the clause number and a one-line summary
      that preserves binding verbs and all conditions; or a verbatim quoted clause when needed.
    error_handling: |
      - If a clause is missing: emit a placeholder noting it is missing and flag needs_review.
      - If summarization risks meaning loss: quote the clause verbatim and mark quoted.

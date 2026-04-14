skills:
  - name: retrieve_policy
    description: Load the policy text file and return its numbered clauses as structured sections.
    input: Plain-text policy file path ending in .txt.
    output: Ordered list of numbered clauses with section number and clause text.
    error_handling: If the file is missing or a clause cannot be parsed, stop with a clear error instead of generating an incomplete summary.

  - name: summarize_policy
    description: Transform structured policy clauses into a clause-referenced summary that preserves meaning.
    input: Ordered list of numbered policy clauses.
    output: Summary text with one line per clause and explicit flags for verbatim clauses when needed.
    error_handling: If summarization would drop a condition or approver, emit the original clause verbatim and mark it as flagged.

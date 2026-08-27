skills:
  - name: retrieve_policy
    description: Load a plain-text HR leave policy document and structure it into numbered policy clauses for downstream summarization.
    input: A plain-text HR leave policy document containing clauses such as 2.3, 2.4, 5.2, and 7.2.
    output: A structured representation of the document with clause numbers, source text, and any clearly identified multi-condition obligations.
    error_handling: If the document is missing, unreadable, or lacks required clauses, return a clear error and do not infer missing policy content.

  - name: summarize_policy
    description: Produce a policy summary that preserves all required clauses by number, keeps every condition intact, and uses verbatim fallback when a clause cannot be safely condensed.
    input: The structured policy clauses from retrieve_policy plus the required clause list: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2.
    output: A compliant summary text that includes each required clause by number, preserves full multi-condition obligations, and flags any clause that must remain verbatim.
    error_handling: If a required clause is missing or ambiguous, do not guess; mark it as missing or unclear and preserve the source wording when possible.

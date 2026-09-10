# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections keyed by clause number.
    input: `input_path` (path to a .txt policy file containing numbered clauses like 2.3).
    output: An ordered mapping of clause number to full clause text, plus the document header lines.
    error_handling: Refuses with a clear error when the file is missing, unreadable, or contains no numbered clauses; never returns guessed content.

  - name: summarize_policy
    description: Turns structured policy sections into a compliant summary with every clause cited and binding conditions preserved.
    input: Ordered clause mapping from retrieve_policy.
    output: A plain-text summary where each numbered clause appears once with a [Clause N] tag, dual-condition clauses are quoted verbatim and flagged, and no sentence adds information absent from the source.
    error_handling: Fails loudly instead of emitting an incomplete summary when any parsed clause has no summary mapping; appends [QUOTED VERBATIM — MEANING-LOSS RISK] to verbatim-quoted clauses rather than compressing them.

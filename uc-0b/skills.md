skills:
  - name: retrieve_policy
    description: Loads a strictly formatted .txt policy file and returns its content as structured numbered sections parsed by clause numbers.
    input: String path to the raw text document
    output: Dictionary mapping clause numbers (e.g. '2.3') to the full extracted textual content of that clause.
    error_handling: Ignores non-clause text elements and headers, preserving only cleanly numbered clauses.

  - name: summarize_policy
    description: Takes structured clause sections and produces a compliant summary incorporating precise clause references.
    input: Dictionary of structured numbered sections.
    output: A single formatted text summary string directly referencing all mandatory clauses.
    error_handling: Explicitly tags any missing mandated clauses with [MISSING FROM SOURCE] and quotes verbatim if rewriting risks dropping conditions.

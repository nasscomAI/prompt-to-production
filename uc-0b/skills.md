# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Absolute or relative path to a .txt policy document (string).
    output: A sequence of clause objects, each with a clause_id (string) and content (string).
    error_handling: If the path does not exist or the file cannot be read, return a clear error and halt; do not guess content.

  - name: summarize_policy
    description: Takes a structured set of policy sections and produces a compliant summary that preserves every clause, all multi-condition obligations, and never adds external information.
    input: A sequence of clause objects as produced by retrieve_policy.
    output: A plain-text summary string. Every source clause appears. Multi-condition obligations render all conditions. If a clause cannot be summarised without meaning loss, it is quoted verbatim and flagged with [VERBATIM].
    error_handling: If input is missing or has zero clauses, return an error. If a clause_id is non-numeric or malformed, include it as-is with a [MALFORMED ID] flag attached.

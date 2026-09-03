skills:
  - name: retrieve_policy
    description: Loads the supplied .txt HR policy and returns its numbered clauses as structured sections.
    input:
      type: string
      format: "Path to a UTF-8 .txt policy file."
    output:
      type: list
      format: "Structured numbered sections containing clause reference and source text."
    error_handling: >
      If the file cannot be read, is empty, or contains no numbered clauses,
      return an error instead of inventing policy content.

  - name: summarize_policy
    description: Produces a clause-complete policy summary while preserving every obligation and condition.
    input:
      type: list
      format: "Structured policy sections containing clause references and source text."
    output:
      type: string
      format: "Clause-referenced text summary containing every numbered clause."
    error_handling: >
      If a clause cannot be summarized without meaning loss, preserve that
      clause verbatim and flag it for review. Never silently omit conditions,
      approvers, thresholds, deadlines, exceptions, or binding requirements.
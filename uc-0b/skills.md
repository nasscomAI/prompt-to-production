# skills.md

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content as structured numbered sections.
    input: File path (string) to a UTF-8 .txt policy document containing numbered clauses such as "2.3".
    output: Ordered mapping of clause_id -> clause_text, where clause_text is the full clause including all wrapped continuation lines; unnumbered decorative lines are dropped.
    error_handling: If the file is missing, unreadable, empty, or contains no numbered clauses, stop and report the error — never return an empty structure or guess content.

  - name: summarize_policy
    description: Produces a meaning-preserving summary of structured policy sections with explicit clause references.
    input: Structured sections from retrieve_policy (clause_id -> clause_text).
    output: Plain-text summary in which every source clause_id appears exactly with its reference, all conditions and binding verbs preserved (must stays must, may stays may, "not permitted" stays not permitted); clauses that cannot be summarised without meaning loss are quoted verbatim and flagged [VERBATIM].
    error_handling: Self-check that every source clause_id is present in the output; if any are missing or a condition would be dropped, regenerate for only those clauses rather than paraphrasing loosely. Never add information absent from the input.

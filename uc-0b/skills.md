# skills.md
# UC-0B Policy summarization skills definitions.

skills:
  - name: retrieve_policy
    description: Load a plain-text policy document and return a mapping of numbered clauses.
    input: Path to a policy text file.
    output: Dict mapping clause numbers (strings like '2.3') to clause text (string).
    error_handling: If file missing or no numbered clauses found, raise an error and return an empty mapping.

  - name: summarize_policy
    description: Produce a conservative, verifiable summary that preserves clause meaning.
    input: Dict of numbered clauses as produced by `retrieve_policy`.
    output: Dict mapping clause numbers to (summary_text, needs_flag) where `needs_flag` is True if the clause was quoted and marked for review.
    error_handling: If a clause appears to contain multi-condition obligations, return the clause verbatim and set `needs_flag` to True.

skills:
  - name: retrieve_policy
    description: Reads the supplied policy text file and extracts its numbered clauses while preserving clause numbers, section identity, ordering, and source wording.
    input: A string input_path pointing to the policy text file.
    output: A structured mapping containing each clause number, its section, and its corresponding source text.
    error_handling: >
      If the file is missing, unreadable, empty, or malformed, raise a clear
      error rather than inventing or approximating policy content. Programming
      and runtime errors must propagate to the caller.

  - name: summarize_policy
    description: Produces a meaning-preserving summary of the required policy clauses while preserving obligations, conditions, consequences, thresholds, and prohibitions.
    input: Structured policy clauses produced by retrieve_policy.
    output: A string containing a concise summary with explicit references to all 10 required clauses.
    error_handling: >
      If any required clause is absent, raise an error. If a clause cannot be
      summarized without losing material meaning, quote that clause verbatim
      and mark it for review rather than guessing or weakening it. Do not
      suppress programming or runtime failures.

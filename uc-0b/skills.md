skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and returns its content parsed as structured numbered sections.
    input:
      type: string
      format: File path to a plain-text policy document containing numbered clauses (e.g. policy_hr_leave.txt).
    output:
      type: dict
      format: Dictionary mapping clause numbers (e.g. "2.3", "5.2") to their full text as strings.
    error_handling: >
      Aborts with a clear error message if the file path does not exist or cannot be read.
      Flags a warning if no numbered clauses are detected in the document, as this may
      indicate a wrong file or unparseable format. Never proceeds silently on an empty result.

  - name: summarize_policy
    description: Takes structured numbered policy sections and produces a clause-complete compliant summary with clause references, preserving all binding obligations and conditions.
    input:
      type: dict
      format: Dictionary mapping clause numbers to their full text, as returned by retrieve_policy.
    output:
      type: string
      format: Plain-text summary where each clause is referenced by number, binding verbs are preserved, all conditions are retained, and any verbatim-quoted clauses are flagged with [VERBATIM — meaning-loss risk].
    error_handling: >
      If a clause cannot be summarised without dropping a condition or softening a binding verb,
      quotes it verbatim and appends [VERBATIM — meaning-loss risk].
      Raises a warning if the output clause count does not match the input clause count,
      indicating a potential clause omission.
      Never adds information outside the source document — any detected scope bleed phrases
      (e.g. "standard practice", "typically", "generally expected") cause that sentence to be
      removed and flagged.
skills:
  - name: retrieve_policy
    description: >
      Load a .txt policy document and return its content as structured
      numbered sections and clauses.
    input: >
      input_path (str) — path to the policy .txt file
    output: >
      dict — section headers mapped to lists of clause dicts with clause_id,
      text, and section name
    error_handling: >
      If file is missing or empty, raise FileNotFoundError with a clear message.
      If file cannot be parsed into numbered clauses, return raw text under a
      "raw" key and flag the output.

  - name: summarize_policy
    description: >
      Take structured sections and produce a compliant summary that preserves
      every clause, all conditions, and all binding verbs with zero scope bleed.
    input: >
      dict — structured policy sections from retrieve_policy
    output: >
      str — formatted summary text with clause references and obligations
    error_handling: >
      If a clause contains conditions that cannot be fully preserved in summary
      form, quote the clause verbatim and flag with [VERBATIM]. Never silently
      drop or generalize a condition.

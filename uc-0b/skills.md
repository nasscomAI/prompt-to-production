skills:
  - name: retrieve_policy
    description: >
      Load a .txt policy file and return its content as structured numbered
      sections with clause references preserved.
    input: >
      Path to a .txt policy document.
    output: >
      A list of section dicts, each with section_title (str), section_number (str),
      and clauses (list of clause dicts with clause_id, text).
    error_handling: >
      If the file does not exist or cannot be read, raise a clear error with the
      expected path. If the file is empty, return an empty list.

  - name: summarize_policy
    description: >
      Take structured policy sections and produce a compliant summary that
      preserves every numbered clause with all conditions intact.
    input: >
      A list of section dicts as produced by retrieve_policy.
    output: >
      A string summary where each numbered clause is represented. Multi-condition
      obligations retain all conditions. If meaning loss is unavoidable, the
      clause is quoted verbatim and flagged [VERBATIM].
    error_handling: >
      If input is empty, return a message stating no clauses to summarise.
      Never add information not present in the source.

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured numbered
      sections with clause references.
    input: >
      A file path (string) pointing to a .txt policy document written in the
      City Municipal Corporation policy format.
    output: >
      A dictionary mapping section numbers to their text content, preserving
      all clause numbers (e.g., "2.3", "5.2") and verbatim wording.
    error_handling: >
      If the file does not exist, raise FileNotFoundError with the path. If the
      file is not a .txt file, raise ValueError. If the file is empty, raise
      ValueError with a message that no policy content was found.

  - name: summarize_policy
    description: >
      Takes structured policy sections and produces a compliant summary that
      preserves every numbered clause, all multi-condition obligations, and
      never adds information absent from the source.
    input: >
      A dictionary of structured numbered sections (output of retrieve_policy).
    output: >
      A plain-text summary string. Every numbered clause from the source must
      appear. Multi-condition obligations must retain all conditions. If a
      clause cannot be summarised without meaning loss, it must be quoted
      verbatim and flagged with [VERBATIM].
    error_handling: >
      If the input is empty or missing required clauses, raise ValueError
      listing the missing clause numbers. If any clause text is modified in a
      way that drops a condition, the skill must refuse and flag the specific
      condition that was dropped.

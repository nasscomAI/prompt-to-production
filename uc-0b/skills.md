# skills.md

skills:
  - name: retrieve_policy
    description: >
      Load a .txt policy file and return its content as structured numbered
      sections with line references.
    input: |
      file_path (str) — path to the .txt policy document.
    output: |
      str — full text of the policy document, unmodified.
    error_handling: >
      If file is missing or unreadable, raise FileNotFoundError with a
      descriptive message. Do not proceed with empty content.

  - name: summarize_policy
    description: >
      Take the full policy text and produce a compliant clause-by-clause
      summary covering all 10 clauses from the inventory, preserving every
      condition and citing source section numbers.
    input: |
      str — full policy text as returned by retrieve_policy.
    output: |
      str — line-separated summary with each clause as:
      "Section X.X: [obligation summary]"
      Multi-condition obligations include ALL conditions.
      Clauses that cannot be simplified are quoted verbatim with [VERBATIM].
    error_handling: >
      If fewer than 10 clauses are produced, append the missing clause
      numbers as errors. Never silently drop a clause.

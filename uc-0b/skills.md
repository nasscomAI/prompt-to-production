skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured
      numbered sections with their constituent clauses.
    input: >
      A file path (string) pointing to a .txt policy document with
      numbered clauses (e.g., 2.3, 5.2) under section headings.
    output: >
      A list of section objects, each containing a section title and a
      list of clause objects (number, text).
    error_handling: >
      If the file does not exist or cannot be read, raise FileNotFoundError
      with a clear message. If the file is empty, return an empty list.

  - name: summarize_policy
    description: >
      Takes structured sections from retrieve_policy and produces a
      compliant text summary with every numbered clause, its exact
      obligations, and verbatim quotes with flags where needed.
    input: >
      A list of section objects (title, clauses) as returned by
      retrieve_policy.
    output: >
      A plain-text summary string. Each clause appears by its number
      with its obligation restated. Multi-condition clauses preserve
      ALL conditions. Clauses whose meaning would be lost in paraphrase
      are quoted verbatim and marked with [FLAGGED — verbatim quote].
    error_handling: >
      If input is empty, return a message stating no clauses found.
      If a clause text is malformed, include it as-is and flag it.

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file from the filesystem and returns its
      content as structured numbered sections.
    input: >
      A filesystem path (string) pointing to a .txt policy file.
    output: >
      A dictionary mapping section headings (e.g. "2. ANNUAL LEAVE") to
      their numbered sub-clauses as a list of strings. Returns
      {"error": "File not found"} if the path does not exist.
    error_handling: >
      If the file does not exist, return {"error": "File not found"}.
      If the file is empty or not valid UTF-8, return {"error": "Invalid
      file"}.

  - name: summarize_policy
    description: >
      Takes structured numbered sections from retrieve_policy and
      produces a compliant summary that preserves every numbered clause
      and all multi-condition obligations.
    input: >
      A dictionary as returned by retrieve_policy: section headings
      mapped to lists of numbered clause strings.
    output: >
      A plain-text summary string where every numbered clause from the
      input is represented, all conditions are preserved, and no
      hallucinated content is added. If any clause must be quoted
      verbatim, it is prefixed with "[VERBATIM]".
    error_handling: >
      If input is not a valid dictionary with numbered clause entries,
      return "ERROR: Invalid input format. Expected structured sections
      with numbered clauses."

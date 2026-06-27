skills:
  - name: retrieve_policy
    description: >
      Load a .txt policy file and return its content as structured
      numbered sections, preserving clause hierarchy.
    input: >
      String: path to .txt file.
    output: >
      Dict mapping section headings to lists of clause dicts, each
      with keys: clause_id (str), text (str).
    error_handling: >
      If file not found or empty, raise FileNotFoundError /
      ValueError with a clear message.

  - name: summarize_policy
    description: >
      Given structured policy sections, produce a summary that covers
      every target clause with full obligations preserved.
    input: >
      Dict from retrieve_policy and a list of target clause IDs to
      include.
    output: >
      String summary with each target clause listed as
      "Clause X.Y: <obligation>" — multi-condition obligations list
      all conditions. Clauses that cannot be safely condensed are
      quoted verbatim and marked [QUOTED].
    error_handling: >
      If a target clause ID is not found in the source, raise
      ValueError listing the missing clauses.

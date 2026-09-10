# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered sections and clauses.
    input: path (str) to a policy .txt file using the "N. TITLE" section / "N.N text" clause format.
    output: list of section dicts — {number (str), title (str), clauses [{number (str), text (str)}]} — in document order.
    error_handling: Raises IOError with a clear message if the file is missing or unreadable; raises ValueError if zero N.N clause patterns are found, rather than silently returning an empty summary for a malformed document.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a clause-referenced summary text, one heading per section and one bullet per clause, with clause text preserved verbatim.
    input: the list of section dicts returned by retrieve_policy.
    output: a single string — "## N. TITLE" per section, followed by "- N.N <clause text>" per clause, covering every clause exactly once.
    error_handling: Skips emitting a heading for any section that has zero parsed clauses (never prints an empty section); never fabricates a clause not present in the input structure.

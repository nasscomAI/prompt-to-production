# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its full content as a string.
    input: input_path (str) — path to the policy .txt file.
    output: Full file content as a single string with all sections intact.
    error_handling: If file not found or unreadable, raises IOError with path info.

  - name: summarize_policy
    description: Takes full policy content and produces a clause-complete, obligation-preserving summary with clause references.
    input: content (str) — full text of the policy document.
    output: Formatted summary string with all numbered clauses, binding obligations marked, and a compliance note listing verified clauses.
    error_handling: If a clause cannot be summarised without meaning loss, quotes it verbatim and flags it as [VERBATIM — OBLIGATION].
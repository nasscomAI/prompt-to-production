# skills.md — UC-0B Policy Summarization Skills

skills:
  - name: retrieve_policy
    description: Load a plain-text policy file and return a mapping of
      numbered clauses to their full text (including indented continuation
      lines).
    input: file path (str) to a .txt policy document.
    output: dict mapping clause_id (e.g. '2.3') -> clause_text (str).
    error_handling: If file cannot be read, raise FileNotFoundError. If the
      file contains no numbered clauses, return an empty dict and surface a
      clear warning.

  - name: summarize_policy
    description: Produce a clause-by-clause summary preserving meaning and
      conditions from the supplied clause mapping.
    input: dict of clause_id -> clause_text, plus an ordered list of
      required_clause_ids to include in the summary.
    output: tuple(summary_lines: list[str], notes: list[str]) where each
      summary_line contains either a paraphrase or the original clause (if
      verbatim), and notes contains any missing-clause or verbatim flags.
    error_handling: For any required clause not found, add a missing-clause
      note and continue. If paraphrasing is ambiguous, include the original
      clause verbatim and add a 'VERBATIM' note.

enforcement_checklist:
  - "All required clauses must be present in the output (or flagged missing)."
  - "No new information introduced beyond the original clause text."
  - "Multi-condition clauses preserved exactly or quoted verbatim."

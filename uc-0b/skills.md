# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file, parses it into structured numbered sections with clause text.
    input: file_path (str) — path to policy .txt file
    output: dict mapping clause numbers (e.g., "2.3") to clause text (str), plus metadata (document title, version, effective date)
    error_handling: If file not found, raise FileNotFoundError. If file is empty or has no numbered clauses, return error dict with flag: NO_CLAUSES_FOUND.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clauses, conditions, and binding verbs.
    input: dict of clause_number -> clause_text (from retrieve_policy), optionally with metadata
    output: str — summary text with clause inventory table, clause-by-clause summaries, and [VERBATIM_REQUIRED] flags where meaning would be lost
    error_handling: If input dict is empty or malformed, return error summary with flag: INVALID_INPUT. If a clause's meaning cannot be preserved, quote verbatim and flag.

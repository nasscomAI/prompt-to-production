skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered sections/clauses.
    input: "file_path (str, path to a policy .txt file)."
    output: "list of dicts, each with keys: clause_number (str, e.g. '5.2'), text (str, full clause text with wrapped lines joined into one string)."
    error_handling: "If the file is missing or unreadable, raises FileNotFoundError with the path. If no numbered clauses are found, returns an empty list rather than raising."

  - name: summarize_policy
    description: Takes structured clause sections and produces a compliant summary, one line per clause, with clause references.
    input: "list of clause dicts as returned by retrieve_policy (clause_number, text)."
    output: "str — the full summary text, one 'Clause X.Y: ...' line per input clause, in clause-number order."
    error_handling: "If a clause has multiple conditions that cannot be safely condensed (detected via multi-condition markers like 'and', 'both', multiple numeric thresholds), it is output verbatim and prefixed with '[VERBATIM]' instead of being paraphrased."

# skills.md — UC-0B Policy Summarizer Skills

skills:
  - name: retrieve_policy
    description: Reads the raw policy text file, parses sections and numbered clauses (e.g., 2.3, 5.2), and returns structured clause dictionary mapping section IDs to clause text.
    input: file_path (str path to policy text file).
    output: Dictionary mapping clause numbers (e.g. '2.3', '5.2') to full clause text strings.
    error_handling: Raises FileNotFoundError if file is missing, or ValueError if section formatting cannot be parsed.

  - name: summarize_policy
    description: Takes structured policy clauses, applies RICE enforcement rules, ensures 100% preservation of binding verbs and multi-condition rules, and generates formatted summary text.
    input: Dictionary of structured policy clauses.
    output: String representing complete, compliant summary text with clause citations.
    error_handling: If critical clauses (e.g., 5.2, 7.2) are missing, flags missing section and includes verbatim quotation fallback.

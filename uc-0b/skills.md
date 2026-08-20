# skills.md — UC-0B HR Policy Summarizer Skills

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses content into structured sections and numbered clauses.
    input: Path to policy text file (str).
    output: Data structure mapping section headers and clause numbers to raw clause text strings.
    error_handling: Raises FileNotFoundError if input file path is invalid, flagging missing document.

  - name: summarize_policy
    description: Generates a complete policy summary ensuring all numbered clauses, binding verbs, and multi-condition rules are preserved.
    input: Parsed policy sections dictionary from retrieve_policy.
    output: Formatted summary text preserving every clause number, binding verb, and approval condition.
    error_handling: If a clause contains ambiguous phrasing, quotes the clause verbatim and appends a [VERBATIM QUOTE - AMBIGUOUS] flag.

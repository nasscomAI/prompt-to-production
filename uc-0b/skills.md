# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and parses it into structured numbered sections (section number, heading, clause number, clause text).
    input: file path (str) to a policy .txt file using the "N.M clause text" numbering convention.
    output: >
      list of dicts, one per clause: {section: "2", heading: "ANNUAL LEAVE",
      clause: "2.3", text: "Employees must submit a leave application at
      least 14 calendar days in advance using Form HR-L1."}.
    error_handling: >
      If the file is missing or a line cannot be matched to the numbering
      pattern, that line is skipped and logged — retrieval still returns
      every clause it could parse rather than failing the whole load.

  - name: summarize_policy
    description: Takes the structured clause list from retrieve_policy and produces a compliant summary that keeps every tracked clause and every condition on it, per the enforcement rules in agents.md.
    input: structured clause list (from retrieve_policy) plus the set of clause numbers that must be tracked (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2).
    output: >
      plain-text summary, one line per tracked clause, each line prefixed
      with its clause number and retaining the original binding verb and
      all conditions.
    error_handling: >
      If a tracked clause number is not found in the parsed document, the
      summary explicitly states "Clause [N] not found in source" rather
      than omitting it silently — a missing clause must be visible, never
      silent.

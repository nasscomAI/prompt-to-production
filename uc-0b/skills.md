# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Ingests a raw policy text file and parses its contents into structured numbered clauses with metadata.
    input: file_path (str) - path to policy .txt document
    output: dict mapping clause numbers (e.g. '2.3', '5.2') to their exact clause body text
    error_handling: Raises FileNotFoundError with a descriptive error if the path does not exist; returns an empty mapping if no numbered clauses are matched.

  - name: summarize_policy
    description: Transforms structured clause records into a verified summary preserving all obligations, dual approvals, and deadlines.
    input: clauses (dict) - structured map of clause numbers to clause text
    output: formatted string summary with strict clause citations and all conditions intact
    error_handling: Flags missing or unparseable clauses and quotes complex legal conditions verbatim to prevent semantic loss.

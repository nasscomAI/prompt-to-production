skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured sections and numbered clauses.
    input:
      type: string
      format: "The absolute or relative path to the policy text file (e.g., policy_hr_leave.txt)."
    output:
      type: dict
      format: "A dictionary mapping section headings to dictionaries of clause numbers and their raw text."
    error_handling: >
      If the file is not found, raise a FileNotFoundError. If the file contains malformed sections, log a warning and capture all raw text under a default 'Uncategorized' section.

  - name: summarize_policy
    description: Takes the structured policy sections/clauses and produces a concise summary with exact clause references, preserving all binding constraints.
    input:
      type: dict
      format: "A structured dictionary of sections and clauses returned by retrieve_policy."
    output:
      type: string
      format: "A formatted markdown or text summary containing every numbered clause, using original binding verbs, and highlighting any verbatim quotes."
    error_handling: >
      If a clause cannot be compressed without dropping key obligations or conditions (e.g., dual-approval constraints), it quotes the clause verbatim and appends a '[VERBATIM]' flag.

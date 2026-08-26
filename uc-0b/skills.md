# skills.md

skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and extracts numbered clauses into a structured map.
    input: Path to policy_hr_leave.txt.
    output: Dictionary mapping clause numbers to clause text.
    error_handling: Raises an informative error if required clauses cannot be parsed or are missing.

  - name: summarize_policy
    description: Produces a compliant summary from structured policy sections, preserving clause references.
    input: Dictionary of numbered clauses from retrieve_policy.
    output: A text summary containing all required clauses and a closing verification note.
    error_handling: Raises an error if a required clause is missing or if summary generation would omit a required obligation.
